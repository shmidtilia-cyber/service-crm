from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(slots=True)
class Listing:
    source: str
    external_id: str
    url: str
    model: str
    year: int
    price: int
    mileage: int
    owners: int | None = None
    seller_type: str | None = None
    city: str | None = None
    engine: str | None = None
    transmission: str | None = None
    trim: str | None = None
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScoredListing:
    listing: Listing
    score: int
    positives: list[str]
    risks: list[str]


def score_listing(item: Listing) -> ScoredListing:
    score = 50
    positives: list[str] = []
    risks: list[str] = []
    model = item.model.casefold()

    if "coolray" in model:
        if 2022 <= item.year <= 2024:
            score += 12; positives.append("подходящий год")
        if item.mileage <= 80_000:
            score += 14; positives.append("пробег до 80 тыс км")
        elif item.mileage <= 100_000:
            score += 4
        else:
            score -= 15; risks.append("большой пробег")
        if item.price <= 1_400_000:
            score += 10; positives.append("в бюджете")

    elif "cs35" in model:
        if 2019 <= item.year <= 2022:
            score += 10; positives.append("подходящий год")
        if item.mileage <= 90_000:
            score += 12; positives.append("нормальный пробег")
        if item.engine and "1.6" in item.engine:
            score += 8; positives.append("атмосферный 1.6")
        else:
            risks.append("проверить двигатель")
        if item.transmission and any(x in item.transmission.casefold() for x in ("aisin", "автомат", "акпп")):
            score += 8; positives.append("классический автомат")
        else:
            risks.append("проверить тип коробки")

    elif "atlas" in model:
        if 2018 <= item.year <= 2022:
            score += 8; positives.append("подходящий год")
        if item.mileage <= 120_000:
            score += 10; positives.append("допустимый пробег")
        if item.engine and "2.4" in item.engine:
            score += 10; positives.append("приоритетный мотор 2.4")
        if item.transmission and any(x in item.transmission.casefold() for x in ("автомат", "акпп")):
            score += 7; positives.append("классический автомат")

    if item.owners == 1:
        score += 10; positives.append("один владелец")
    elif item.owners == 2:
        score += 3
    elif item.owners and item.owners > 2:
        score -= 10; risks.append("много владельцев")

    if item.seller_type == "private":
        score += 5; positives.append("частный продавец")
    elif item.seller_type == "official_dealer":
        score += 4; positives.append("официальный дилер")
    elif item.seller_type == "dealer":
        risks.append("уточнить цену без кредита и трейд ин")

    if item.city and any(x in item.city.casefold() for x in ("москва", "москов")):
        score += 5; positives.append("Москва или МО")
    else:
        risks.append("проверить расстояние до Москвы")

    if item.price < 750_000:
        score -= 20; risks.append("подозрительно низкая цена")

    return ScoredListing(item, max(0, min(100, score)), positives, risks)


def select_best(items: Iterable[Listing], minimum: int = 75) -> list[ScoredListing]:
    scored = [score_listing(item) for item in items]
    return sorted((x for x in scored if x.score >= minimum), key=lambda x: x.score, reverse=True)
