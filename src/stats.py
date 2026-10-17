BOLD = "\033[1m"
RESET = "\033[0m"

# Position of each field in an eSIM row (see read_data.py)
PROVIDER = 1
COUNTRY = 2
DATA_GB = 3
VALIDITY = 4
PRICE = 5
NETWORK = 6


def total_count(esims):
    return len(esims)


def count_above(esims, threshold):
    count = 0
    for esim in esims:
        if esim[PRICE] > threshold:
            count += 1
    return count


def price_range(esims):
    cheapest = esims[0]
    priciest = esims[0]
    for esim in esims:
        if esim[PRICE] < cheapest[PRICE]:
            cheapest = esim
        if esim[PRICE] > priciest[PRICE]:
            priciest = esim
    return cheapest, priciest


def average_data(esims):
    """Average GB per card. Unlimited plans (None) are left out."""
    total = 0
    counted = 0
    for esim in esims:
        if esim[DATA_GB] is not None:
            total += esim[DATA_GB]
            counted += 1
    return total / counted, counted


def average_price(esims):
    total = 0
    for esim in esims:
        total += esim[PRICE]
    return total / len(esims)


def count_by_provider(esims):
    counts = {}
    for esim in esims:
        provider = esim[PROVIDER]
        counts[provider] = counts.get(provider, 0) + 1
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)


def average_price_by_provider(esims):
    sums = {}
    counts = {}
    for esim in esims:
        provider = esim[PROVIDER]
        sums[provider] = sums.get(provider, 0) + esim[PRICE]
        counts[provider] = counts.get(provider, 0) + 1
    averages = []
    for provider in sums:
        averages.append((provider, sums[provider] / counts[provider]))
    return sorted(averages, key=lambda item: item[1])


def price_per_gb_by_provider(esims):
    """Total price / total GB per provider. Unlimited plans (None) are left out."""
    prices = {}
    gigas = {}
    for esim in esims:
        if esim[DATA_GB] is None or esim[DATA_GB] == 0:
            continue
        provider = esim[PROVIDER]
        prices[provider] = prices.get(provider, 0) + esim[PRICE]
        gigas[provider] = gigas.get(provider, 0) + esim[DATA_GB]
    result = []
    for provider in prices:
        result.append((provider, prices[provider] / gigas[provider]))
    return sorted(result, key=lambda item: item[1])


def format_data(data_gb):
    if data_gb is None:
        return "Unlimited"
    return f"{data_gb:g} GB"


def stats_by_country(esims):
    """One entry per country: what is available there, in price and GB / unlimited."""
    countries = {}
    for esim in esims:
        name = esim[COUNTRY]
        if name not in countries:
            countries[name] = {"country": name, "cards": 0, "providers": set(),
                               "cheapest": None, "best_price_per_gb": None,
                               "unlimited_cards": 0, "cheapest_unlimited": None}
        c = countries[name]
        c["cards"] += 1
        c["providers"].add(esim[PROVIDER])
        if c["cheapest"] is None or esim[PRICE] < c["cheapest"]:
            c["cheapest"] = esim[PRICE]
        if esim[DATA_GB] is None:
            c["unlimited_cards"] += 1
            if c["cheapest_unlimited"] is None or esim[PRICE] < c["cheapest_unlimited"]:
                c["cheapest_unlimited"] = esim[PRICE]
        elif esim[DATA_GB] > 0:
            ratio = esim[PRICE] / esim[DATA_GB]
            if c["best_price_per_gb"] is None or ratio < c["best_price_per_gb"]:
                c["best_price_per_gb"] = ratio
    result = []
    for name in sorted(countries):
        c = countries[name]
        c["providers"] = len(c["providers"])
        result.append(c)
    return result


def compute_stats(esims):
    """Gather every statistic in one dictionary, for dashboard.py."""
    cheapest, priciest = price_range(esims)
    avg_gb, limited_count = average_data(esims)
    return {
        "total": total_count(esims),
        "above_100": count_above(esims, 100),
        "cheapest": cheapest,
        "priciest": priciest,
        "avg_gb": avg_gb,
        "limited_count": limited_count,
        "unlimited_count": len(esims) - limited_count,
        "avg_price": average_price(esims),
        "by_provider": count_by_provider(esims),
        "avg_price_by_provider": average_price_by_provider(esims),
        "price_per_gb": price_per_gb_by_provider(esims),
        "by_country": stats_by_country(esims),
    }


if __name__ == "__main__":
    from read_data import load_all
    esims = load_all('dataset') #invalid_dataset

    print(f"{BOLD}1. Total eSIM cards:{RESET} {total_count(esims)}")
    print(f"{BOLD}2. Cards above 100 €:{RESET} {count_above(esims, 100)}")

    cheapest, priciest = price_range(esims)
    print(f"{BOLD}3. Price range:{RESET} {cheapest[PRICE]:.2f} € - {priciest[PRICE]:.2f} €")
    print(f"   Cheapest: {cheapest[PROVIDER]}, {cheapest[COUNTRY]}, "
          f"{format_data(cheapest[DATA_GB])}, {cheapest[VALIDITY]} days")
    print(f"   Priciest: {priciest[PROVIDER]}, {priciest[COUNTRY]}, "
          f"{format_data(priciest[DATA_GB])}, {priciest[VALIDITY]} days")

    avg_gb, counted = average_data(esims)
    print(f"{BOLD}4. Average data per card:{RESET} {avg_gb:.2f} GB "
          f"(on {counted} limited plans, {len(esims) - counted} unlimited excluded)")

    print(f"{BOLD}5. Average price:{RESET} {average_price(esims):.2f} €")

    print(f"{BOLD}6. Cards per provider:{RESET}")
    for provider, count in count_by_provider(esims):
        print(f"   {provider}: {count}")

    print(f"{BOLD}7. Average price per provider:{RESET}")
    for provider, average in average_price_by_provider(esims):
        print(f"   {provider}: {average:.2f} €")

    print(f"{BOLD}8. Price per GB by provider (limited plans only):{RESET}")
    for provider, ratio in price_per_gb_by_provider(esims):
        print(f"   {provider}: {ratio:.2f} €/GB")

    print(f"{BOLD}9. Availability by country:{RESET}")
    for c in stats_by_country(esims):
        per_gb = "-" if c["best_price_per_gb"] is None else f'{c["best_price_per_gb"]:.2f}'
        unlimited = "none" if c["cheapest_unlimited"] is None else f'{c["cheapest_unlimited"]:.2f} €'
        print(f'   {c["country"]:20} {c["cards"]:3} cards, {c["providers"]:2} providers, '
              f'from {c["cheapest"]:6.2f} €, best {per_gb} €/GB, '
              f'{c["unlimited_cards"]:2} unlimited (from {unlimited})')
# test
