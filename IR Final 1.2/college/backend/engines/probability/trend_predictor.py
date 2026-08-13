# Trend Predictor
"""
InsightRural 3.0
Trend Predictor

Predicts future closing cutoff using historical data.

Author:
InsightRural
"""

from statistics import mean
from typing import List

from .models import CutoffRecord, TrendResult


class TrendPredictor:

    """
    Predict future cutoff based on previous year cutoffs.

    Uses

    - Moving Average
    - Linear Trend
    - Stability Score

    """

    def __init__(self):

        pass

    def predict(
        self,
        history: List[CutoffRecord]
    ) -> TrendResult:

        if len(history) == 0:

            return TrendResult(
                predicted_cutoff=0,
                moving_average=0,
                slope=0,
                trend="UNKNOWN",
                confidence=0
            )

        history = sorted(history, key=lambda x: x.year)

        cutoffs = [
            item.closing_rank
            for item in history
        ]

        years = [
            item.year
            for item in history
        ]

        moving_avg = mean(cutoffs)

        slope = self.calculate_slope(
            years,
            cutoffs
        )

        predicted = cutoffs[-1] + slope

        confidence = self.calculate_confidence(
            cutoffs
        )

        trend = self.identify_trend(
            slope
        )

        return TrendResult(

            predicted_cutoff=round(predicted),

            moving_average=round(moving_avg),

            slope=round(slope,2),

            trend=trend,

            confidence=round(confidence,2)

        )

    def calculate_slope(
        self,
        years,
        cutoffs
    ):

        n = len(years)

        if n < 2:

            return 0

        x_mean = mean(years)

        y_mean = mean(cutoffs)

        numerator = 0

        denominator = 0

        for x,y in zip(years,cutoffs):

            numerator += (x-x_mean)*(y-y_mean)

            denominator += (x-x_mean)**2

        if denominator == 0:

            return 0

        return numerator/denominator

    def calculate_confidence(
        self,
        cutoffs
    ):

        if len(cutoffs) == 1:

            return 45

        variation = max(cutoffs)-min(cutoffs)

        avg = mean(cutoffs)

        if avg == 0:

            return 0

        ratio = variation/avg

        confidence = 100-(ratio*100)

        confidence=max(
            30,
            min(
                confidence,
                99
            )
        )

        return confidence

    def identify_trend(
        self,
        slope
    ):

        if slope>500:

            return "STRONGLY_INCREASING"

        if slope>100:

            return "INCREASING"

        if slope<-500:

            return "STRONGLY_DECREASING"

        if slope<-100:

            return "DECREASING"

        return "STABLE"
