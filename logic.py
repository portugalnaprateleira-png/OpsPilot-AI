"""Motor de regras determinístico do OpsPilot AI (sem LLM e sem rede)."""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Any

from data import TABLES, REQUIRED

Data = dict[str, list[dict[str, Any]]]


def number(v: Any) -> float:
    try:
        return float(v or 0)
    except (ValueError, TypeError):
        return 0.0


def parse_date(v: Any) -> date | None:
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v)[:10]) if v not in (None, "", "None", "NaT") else None
    except (ValueError, TypeError):
        return None


def within_year(v: Any, today: date) -> bool:
    d = parse_date(v)
    return bool(d and d.year == today.year and d <= today)


def row_lookup(rows: list[dict], key: str = "id") -> dict[str, dict]:
    return {str(row.get(key, "")): row for row in rows if row.get(key)}


def validate_dataset(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["O ficheiro tem de conter um objeto JSON com todas as tabelas."]
    for name, required in REQUIRED.items():
        rows = data.get(name)
        if not isinstance(rows, list):
            errors.append(f"Tabela '{name}': lista em falta.")
            continue
        ids = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append(f"{name}: linha {index + 1} inválida.")
                continue
            for field in required:
                if not str(row.get(field, "")).strip():
                    errors.append(f"{name}: linha {index + 1}, campo obrigatório '{field}'.")
            if row.get("id"):
                ids.append(str(row["id"]))
        if len(ids) != len(set(ids)):
            errors.append(f"{name}: identificadores duplicados.")
    if errors:
        return errors[:25]
    asset_ids = set(row_lookup(data["ativos"]))
    person_ids = set(row_lookup(data["colaboradores"]))
    supplier_ids = set(row_lookup(data["fornecedores"]))
    for name in ("contratos", "utilizacao", "despesas", "multas", "afetacoes", "consumiveis", "manutencoes", "inspecoes", "checklists", "sinistros", "propostas", "telemetria"):
        for row in data[name]:
            if row.get("ativo_id") and row["ativo_id"] not in asset_ids:
                errors.append(f"{name}: ativo inexistente '{row['ativo_id']}'.")
            if row.get("fornecedor_id") and row["fornecedor_id"] not in supplier_ids:
                errors.append(f"{name}: fornecedor inexistente '{row['fornecedor_id']}'.")
            if row.get("operador_id") and row["operador_id"] not in person_ids:
                errors.append(f"{name}: operador inexistente '{row['operador_id']}'.")
    for row in data["ativos"]:
        if row.get("colaborador_id") and row["colaborador_id"] not in person_ids:
            errors.append(f"ativos: colaborador inexistente '{row['colaborador_id']}'.")
    return errors[:25]


def priority(days: int) -> str:
    if days <= 0: return "Crítica — hoje/vencido"
    if days <= 7: return "Alta — 7 dias"
    if days <= 30: return "Média — 30 dias"
    return "Planeada"


def get_alerts(data: Data, horizon: int = 30, today: date | None = None) -> list[dict]:
    if not 1 <= horizon <= 365:
        raise ValueError("Horizonte entre 1 e 365 dias.")
    today = today or date.today()
    alerts: list[dict] = []
    asset_map = row_lookup(data["ativos"])
    staff_map = row_lookup(data["colaboradores"])

    def append(area: str, ref: str, ativo: str, tipo: str, deadline: Any, action: str, motivo: str = ""):
        dd = parse_date(deadline)
        if dd is None:
            return
        days = (dd - today).days
        if days <= horizon:
            alerts.append(dict(area=area, referencia=ref, ativo=ativo, evento=tipo, prazo=dd.isoformat(), dias=days,
                               prioridade=priority(days), acao_proposta=action, motivo=motivo))

    for a in data["ativos"]:
        append("Manutenção", a["id"], a["id"], "Manutenção por calendário", a.get("proxima_manutencao"), "Validar disponibilidade e agendar intervenção")
        if a.get("categoria") == "Viatura" and number(a.get("limite_km_manutencao")) > 0:
            if number(a.get("km_atual")) >= number(a.get("limite_km_manutencao")):
                append("Manutenção", a["id"], a["id"], "Limite de quilómetros atingido", today, "Criar proposta de manutenção por km")
        if a.get("categoria") == "Empilhador" and number(a.get("limite_horas_manutencao")) > 0:
            if number(a.get("horas_atual")) >= number(a.get("limite_horas_manutencao")):
                append("Manutenção", a["id"], a["id"], "Limite de horas atingido", today, "Criar proposta de manutenção por horas")
    for c in data["contratos"]:
        if c.get("estado") == "Ativo":
            append("Contratos", c["id"], c.get("ativo_id", ""), f"Fim de {c.get('tipo', 'contrato')}", c.get("fim"), "Validar renovação/substituição com fornecedor")
            if c.get("devolucao_prevista"):
                append("Contratos", c["id"], c.get("ativo_id", ""), "Devolução prevista", c.get("devolucao_prevista"), "Preparar vistoria e devolução")
    for i in data["inspecoes"]:
        if i.get("estado") != "Concluída":
            append("Conformidade", i["id"], i.get("ativo_id", ""), i.get("tipo", "Inspeção"), i.get("data_limite"), "Validar obrigação aplicável e obter evidência da verificação")
    for p in data["colaboradores"]:
        if p.get("ativo") == "Sim":
            if p.get("carta_valida_ate"):
                append("Habilitações", p["id"], "", "Validade da carta", p["carta_valida_ate"], "Solicitar confirmação documental e atualizar registo", p.get("nome", ""))
            if p.get("formacao_empilhador_ate"):
                append("Habilitações", p["id"], "", "Validade da formação", p["formacao_empilhador_ate"], "Verificar formação/competência e afetação", p.get("nome", ""))
    for a in data["afetacoes"]:
        p = staff_map.get(a.get("operador_id"))
        if p:
            exp = parse_date(p.get("formacao_empilhador_ate"))
            planned = parse_date(a.get("data"))
            if not exp or (planned and exp < planned):
                append("Segurança", a["id"], a.get("ativo_id", ""), "Operador com formação não validada", planned or today, "Rever afetação antes do turno", f"Operador {a.get('operador_id')}")
        asset = asset_map.get(a.get("ativo_id"))
        if asset and asset.get("estado") != "Operacional":
            append("Segurança", a["id"], a.get("ativo_id", ""), "Afetação de equipamento indisponível", a.get("data"), "Replanear turno", asset.get("estado", ""))
    for f in data["multas"]:
        if f.get("estado") != "Concluída":
            append("Multas", f["id"], f.get("ativo_id", ""), "Prazo de resposta à coima", f.get("prazo_resposta"), "Confirmar condutor e preparar comunicação")
    for x in data["consumiveis"]:
        append("Equipamentos", x["id"], x.get("ativo_id", ""), f"Verificação: {x.get('categoria')}", x.get("proxima_verificacao"), "Verificar componente/consumível")
    for c in data["checklists"]:
        if c.get("resultado") == "Não conforme":
            append("Segurança", c["id"], c.get("ativo_id", ""), "Checklist com anomalia", c.get("data"), "Validar risco, registar ação e verificar equipamento")
    for m in data["manutencoes"]:
        if m.get("estado") not in ("Concluída", "Cancelada"):
            append("Manutenção", m["id"], m.get("ativo_id", ""), "Ordem de trabalho pendente", m.get("prevista"), "Confirmar avanço com a oficina")
    # Remove exact duplicate notices in same dimension, not separate contractual obligations.
    alerts.sort(key=lambda x: (x["dias"], x["area"], x["ativo"], x["referencia"]))
    return alerts


def generate_action_plan(data: Data, horizon: int = 30, today: date | None = None) -> list[dict]:
    seen = set()
    result = []
    for alert in get_alerts(data, horizon, today):
        key = (alert["referencia"], alert["evento"])
        if key in seen:
            continue
        seen.add(key)
        result.append({
            "id": f"PLAN-{len(result)+1:03d}", "ativo": alert["ativo"], "area": alert["area"],
            "prioridade": alert["prioridade"], "prazo": alert["prazo"],
            "acao": alert["acao_proposta"], "estado": "Proposta — sem execução",
            "referencia": alert["referencia"],
        })
    return result


def get_compliance_rate(data: Data, today: date | None = None) -> tuple[int, int, float]:
    """Taxa documental: inspeções e contratos vencidos, NÃO parecer legal."""
    today = today or date.today()
    inspected = [x for x in data["inspecoes"] if (parse_date(x.get("data_limite")) or date.max) <= today]
    completed = sum(x.get("estado") == "Concluída" and parse_date(x.get("executada_em")) is not None and parse_date(x.get("executada_em")) <= parse_date(x.get("data_limite")) for x in inspected)
    total = len(inspected)
    return completed, total, round(100 * completed / total, 1) if total else 100.0


def recorded_deadline_compliance(data: Data, today: date | None = None) -> tuple[int, int, float]:
    """Indicador documental sintético conjunto: inspeções e seguros com prazo passado.

    Não valida legislação ou se o seguro está realmente em vigor. 'Renovado' é apenas
    o estado de workflow marcado por quem usa a demo.
    """
    today = today or date.today()
    inspected = [x for x in data["inspecoes"] if (parse_date(x.get("data_limite")) or date.max) <= today]
    insurance_due = [c for c in data["contratos"] if c.get("tipo") == "Seguro" and (parse_date(c.get("fim")) or date.max) <= today]
    good_inspections = sum(x.get("estado") == "Concluída" and parse_date(x.get("executada_em")) is not None
                           and parse_date(x.get("executada_em")) <= parse_date(x.get("data_limite")) for x in inspected)
    good_insurance = sum(c.get("estado") == "Renovado" for c in insurance_due)
    total = len(inspected) + len(insurance_due)
    good = good_inspections + good_insurance
    return good, total, round(100 * good / total, 1) if total else 100.0


def get_maintenance_rate(data: Data, today: date | None = None) -> tuple[int, int, float]:
    today = today or date.today()
    due = [x for x in data["manutencoes"] if x.get("tipo") == "Preventiva" and (parse_date(x.get("prevista")) or date.max) <= today]
    ok = sum(x.get("estado") == "Concluída" and parse_date(x.get("concluida")) is not None and parse_date(x.get("concluida")) <= parse_date(x.get("prevista")) for x in due)
    return ok, len(due), round(100 * ok / len(due), 1) if due else 100.0


def supplier_sla(data: Data) -> list[dict]:
    out = []
    for s in data["fornecedores"]:
        expected = number(s.get("sla_alvo_h"))
        actual = number(s.get("resposta_media_h"))
        out.append({"fornecedor": s.get("nome"), "especialidade": s.get("especialidade"),
                    "avaliacao": number(s.get("pontuacao_1_5")), "sla_alvo_h": expected,
                    "resposta_media_h": actual, "sla": "Dentro" if expected and actual <= expected else "Fora"})
    return out


def operating_indicators(data: Data) -> dict[str, float | int]:
    assets = data["ativos"]
    n = len(assets)
    available = sum(x.get("estado") == "Operacional" for x in assets)
    forklifts = {x["id"] for x in assets if x.get("categoria") == "Empilhador"}
    period = [r for r in data["utilizacao"] if r.get("ativo_id") in forklifts]
    planned = sum(number(r.get("horas_previstas")) for r in period)
    productive = sum(number(r.get("horas_produtivas")) for r in period)
    return {
        "ativos": n, "viaturas": sum(x.get("categoria") == "Viatura" for x in assets),
        "empilhadores": len(forklifts), "disponibilidade_pct": round(100 * available / n, 1) if n else 0,
        "utilizacao_empilhadores_pct": round(100 * productive / planned, 1) if planned else 0,
        "sinistros": len(data["sinistros"]), "custo_sinistros_eur": sum(number(x.get("custo_eur")) for x in data["sinistros"]),
        "horas_imobilizacao": sum(number(x.get("horas_paragem")) for x in data["utilizacao"]),
    }


def _months_overlap_year(start: Any, end: Any, today: date) -> int:
    st = parse_date(start) or date.min
    en = parse_date(end) or date.max
    lo = max(st, date(today.year, 1, 1))
    hi = min(en, today)
    if hi < lo:
        return 0
    return (hi.year - lo.year) * 12 + hi.month - lo.month + 1


def cost_analysis(data: Data, today: date | None = None) -> dict[str, Any]:
    """Custos indicativos YTD: movimento observado + mensalidades estimadas + depreciação linear ilustrativa.

    Dados sintéticos e sem garantia de completude. Nunca duplicar rendas como aquisição.
    """
    today = today or date.today()
    details: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for r in data["despesas"]:
        if within_year(r.get("data"), today):
            details[r.get("ativo_id", "")][r.get("categoria", "Outros")] += number(r.get("valor_eur"))
    for r in data["manutencoes"]:
        if within_year(r.get("abertura"), today):
            details[r.get("ativo_id", "")]["Manutenção"] += number(r.get("custo_eur"))
    for r in data["sinistros"]:
        if within_year(r.get("data"), today):
            details[r.get("ativo_id", "")]["Sinistros"] += number(r.get("custo_eur"))
    for r in data["multas"]:
        if within_year(r.get("data"), today):
            details[r.get("ativo_id", "")]["Multas"] += number(r.get("valor_eur"))
    # Os registos de consumíveis são stock/controlo operacional sem data de aquisição;
    # não são incluídos automaticamente no TCO para evitar dupla contagem.
    rental_assets = set()
    for c in data["contratos"]:
        monthly = number(c.get("mensalidade_eur"))
        if monthly <= 0:
            continue
        count = _months_overlap_year(c.get("inicio"), c.get("fim"), today)
        details[c.get("ativo_id", "")]["Contratos"] += monthly * count
        if c.get("tipo") in ("Renting", "Aluguer", "Leasing", "ALD") and count > 0:
            rental_assets.add(c.get("ativo_id"))
    months_year = today.month  # approximation YTD, annual linear deprecation for demonstration
    for a in data["ativos"]:
        if a["id"] in rental_assets:
            continue
        useful = number(a.get("vida_util_anos"))
        depreciation = max(0, number(a.get("custo_compra_eur")) - number(a.get("valor_residual_eur"))) / useful if useful > 0 else 0
        details[a["id"]]["Depreciação estimada"] += depreciation * months_year / 12
    usage = row_lookup(data["utilizacao"], "ativo_id")
    per_asset = []
    total_by_category: dict[str, float] = defaultdict(float)
    for a in data["ativos"]:
        aid = a["id"]
        categories = details[aid]
        total = sum(categories.values())
        for cat, cost in categories.items():
            total_by_category[cat] += cost
        used = usage.get(aid, {})
        km = number(used.get("km_periodo"))
        h = number(used.get("horas_produtivas"))
        per_asset.append({
            "ativo": aid, "categoria": a.get("categoria"), "tipo_energia": a.get("energia"),
            "tco_ytd_eur": round(total, 2), "km_ytd": km, "horas_ytd": h,
            "eur_km": round(total / km, 3) if km else None,
            "eur_hora": round(total / h, 2) if h else None,
        })
    budgets = {r["categoria"]: number(r.get("orcamento_eur")) for r in data["orcamentos"] if int(number(r.get("ano"))) == today.year}
    cats = sorted(set(budgets) | set(total_by_category))
    comparison = [
        {"categoria": cat, "orcamento_anual_eur": round(budgets.get(cat, 0), 2),
         "custo_ytd_eur": round(total_by_category.get(cat, 0), 2),
         "orcamento_ytd_proporcional_eur": round(budgets.get(cat, 0) * today.month / 12, 2),
         "desvio_ytd_eur": round(total_by_category.get(cat, 0) - budgets.get(cat, 0) * today.month / 12, 2)}
        for cat in cats
    ]
    return {"ativos": per_asset, "categorias": comparison, "total_eur": round(sum(x["tco_ytd_eur"] for x in per_asset), 2),
            "observacao": "Custos YTD indicativos: movimentos + mensalidades aproximadas + depreciação linear. Não inclui todos os custos reais."}


def energy_metrics(data: Data, today: date | None = None) -> dict[str, float]:
    today = today or date.today()
    q = defaultdict(float)
    for row in data["despesas"]:
        if within_year(row.get("data"), today):
            unit = row.get("unidade")
            if unit in ("L", "kWh", "kg"):
                q[unit] += number(row.get("quantidade"))
    driven = sum(number(x.get("km_periodo")) for x in data["utilizacao"] if number(x.get("km_periodo")) > 0)
    return {"litros": q["L"], "kwh": q["kWh"], "kg_gas": q["kg"], "km": driven,
            "litros_100km_agregado": round(100*q["L"]/driven, 2) if driven else 0}


def compare_proposals(data: Data) -> list[dict]:
    names = row_lookup(data["fornecedores"])
    result = []
    for p in data["propostas"]:
        months = number(p.get("prazo_meses"))
        total = number(p.get("entrada_eur")) + number(p.get("mensalidade_eur")) * months
        result.append({"id": p["id"], "fornecedor": names.get(p.get("fornecedor_id"), {}).get("nome", p.get("fornecedor_id")),
                       "ativo": p.get("ativo_id"), "modalidade": p.get("modalidade"), "prazo_meses": months,
                       "manutencao_incluida": p.get("manutencao_incluida"), "custo_nominal_eur": round(total, 2)})
    return sorted(result, key=lambda x: x["custo_nominal_eur"])


def make_maintenance_proposals(data: Data, horizon: int = 30, today: date | None = None) -> int:
    """Creates only internal draft work orders, never external systems; avoids duplicate proposals."""
    today = today or date.today()
    current = {(r.get("ativo_id"), r.get("descricao")) for r in data["manutencoes"]}
    count = 0
    for a in get_alerts(data, horizon, today):
        if a["area"] != "Manutenção" or "Ordem de trabalho pendente" in a["evento"]:
            continue
        description = f"Proposta automática: {a['evento']}"
        key = (a["ativo"], description)
        if key in current:
            continue
        count += 1
        current.add(key)
        data["manutencoes"].append({
            "id": f"AUTO-{today.strftime('%Y%m%d')}-{count:03d}", "ativo_id": a["ativo"],
            "tipo": "Preventiva", "categoria": "Plano", "descricao": description,
            "abertura": today.isoformat(), "prevista": a["prazo"], "concluida": "",
            "fornecedor_id": "", "custo_eur": 0, "horas_paragem": 0,
            "causa": "Por validar", "estado": "Proposta",
        })
    return count
