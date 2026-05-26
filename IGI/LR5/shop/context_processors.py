from .services import get_nbrb_currency_options, get_currency_by_code, get_currency_factor

def currency_context(request):
    selected_currency = request.session.get("selected_currency", "BYN")
    options = get_nbrb_currency_options()
    valid_codes = {item["code"] for item in options}
    if selected_currency not in valid_codes:
        selected_currency = "BYN"
    currency = get_currency_by_code(selected_currency)
    return {
        "currency_options": options,
        "selected_currency": selected_currency,
        "selected_currency_name": currency["name"],
        "currency_factor": get_currency_factor(selected_currency),
    }
