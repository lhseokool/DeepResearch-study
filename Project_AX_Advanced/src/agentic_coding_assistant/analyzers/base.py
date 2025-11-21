"""Base analyzer interface."""

from abc import ABC, abstractmethod

from ..models.schema import AnalysisRequest, AnalysisResult


class BaseAnalyzer(ABC):
    """Base class for code analyzers."""

    @abstractmethod
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Perform impact analysis.

        Args:
            request: Analysis request with parameters

        Returns:
            AnalysisResult with dependencies and metadata
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the analyzer is available.

        Returns:
            True if analyzer can be used, False otherwise
        """
        pass
