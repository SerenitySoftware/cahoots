class ParseResult:
    """Represents a single result from the parsing process"""

    Type = "Unknown"
    Subtype = "Unknown"
    Confidence = 0
    ResultValue = None
    Data = {}

    def __init__(
            self,
            type="Unknown",
            subtype="Unknown",
            confidence=0,
            value=None,
            additional_data={}
    ):
        self.Type = type
        self.Subtype = subtype
        self.Confidence = confidence
        self.ResultValue = value
        self.Data = additional_data
