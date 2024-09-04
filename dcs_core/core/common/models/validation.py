#  Copyright 2022-present, the Waterdip Labs Pvt. Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union


class ConditionType(str, Enum):
    GTE = "gte"
    LTE = "lte"
    GT = "gt"
    LT = "lt"
    EQ = "eq"


@dataclass
class Threshold:
    gte: Optional[float] = None
    lte: Optional[float] = None
    gt: Optional[float] = None
    lt: Optional[float] = None
    eq: Optional[float] = None


@dataclass
class Validation:
    threshold: Threshold


class ValidationFunctionType(str, Enum):
    """
    ValidationFunctionType is an enum that represents the type of validation
    function that is applied to a dataset or a field.
    """

    """
    DATASET validation function type applied to a dataset
    """
    DATASET = "dataset"

    """
    FIELD validation function type applied to a field of the dataset
    """
    FIELD = "field"


class ValidationFunction(str, Enum):
    """
    ValidationType is an enum that represents the type of validation that is generated by a data source.
    """

    # Numeric validations 11
    MIN = "min"
    MAX = "max"
    AVG = "avg"
    SUM = "sum"
    MEDIAN = "median"
    STDDEV = "stddev"
    VARIANCE = "variance"
    COUNT_FALSE = "count_false"
    PERCENT_FALSE = "percent_false"
    COUNT_TRUE = "count_true"
    PERCENT_TRUE = "percent_true"
    PERCENTILE_20 = "percentile_20"
    PERCENTILE_40 = "percentile_40"
    PERCENTILE_60 = "percentile_60"
    PERCENTILE_80 = "percentile_80"
    PERCENTILE_90 = "percentile_90"
    COUNT_ZERO = "count_zero"
    PERCENT_ZERO = "percent_zero"

    # Reliability validations 3
    COUNT_ROWS = "count_rows"
    COUNT_DOCUMENTS = "count_documents"
    FRESHNESS = "freshness"

    # Uniqueness validations 2
    COUNT_DISTINCT = "count_distinct"
    COUNT_DUPLICATE = "count_duplicate"

    # Completeness validations 8
    COUNT_NULL = "count_null"
    COUNT_NOT_NULL = "count_not_null"
    PERCENT_NULL = "percent_null"
    PERCENT_NOT_NULL = "percent_not_null"
    COUNT_EMPTY_STRING = "count_empty_string"
    PERCENT_EMPTY_STRING = "percent_empty_string"
    COUNT_NAN = "count_nan"
    PERCENT_NAN = "percent_nan"

    # Custom SQL
    CUSTOM_SQL = "custom_sql"

    # Validity validations 45
    # ========================================
    COUNT_INVALID_VALUES = "count_invalid_values"
    PERCENT_INVALID_VALUES = "percent_invalid_values"
    COUNT_VALID_VALUES = "count_valid_values"
    PERCENT_VALID_VALUES = "percent_valid_values"
    COUNT_INVALID_REGEX = "count_invalid_regex"
    PERCENT_INVALID_REGEX = "percent_invalid_regex"
    COUNT_VALID_REGEX = "count_valid_regex"
    PERCENT_VALID_REGEX = "percent_valid_regex"

    # -- String Format
    STRING_LENGTH_MAX = "string_length_max"
    STRING_LENGTH_MIN = "string_length_min"
    STRING_LENGTH_AVERAGE = "string_length_average"

    # -- Identification Format

    COUNT_UUID = "count_uuid"
    PERCENT_UUID = "percent_uuid"
    """
    Prem ID (https://permid.org/)
    """
    COUNT_PERM_ID = "count_perm_id"
    PERCENT_PERM_ID = "percent_perm_id"
    """
    SSN (https://en.wikipedia.org/wiki/Social_Security_number#Structure)
    """
    COUNT_SSN = "count_ssn"
    PERCENT_SSN = "percent_ssn"

    # -- Contact Information
    COUNT_USA_PHONE = "count_usa_phone"
    PERCENT_USA_PHONE = "percent_usa_phone"
    COUNT_USA_STATE_CODE = "count_usa_state_code"
    PERCENT_USA_STATE_CODE = "percent_usa_state_code"
    COUNT_USA_ZIP_CODE = "count_usa_zip_code"
    PERCENT_USA_ZIP_CODE = "percent_usa_zip_code"
    COUNT_EMAIL = "count_email"
    PERCENT_EMAIL = "percent_email"

    # -- Financial Information
    """
    https://en.wikipedia.org/wiki/SEDOL
    """
    COUNT_SEDOL = "count_sedol"
    PERCENT_SEDOL = "percent_sedol"
    COUNT_CUSIP = "count_cusip"
    PERCENT_CUSIP = "percent_cusip"
    COUNT_LEI = "count_lei"
    PERCENT_LEI = "percent_lei"
    COUNT_FIGI = "count_figi"
    PERCENT_FIGI = "percent_figi"
    COUNT_ISIN = "count_isin"
    PERCENT_ISIN = "percent_isin"

    # -- Time Format
    COUNT_TIMESTAMP_STRING = "count_timestamp_string"
    PERCENT_TIMESTAMP_STRING = "percent_timestamp_string"
    COUNT_NOT_IN_FUTURE = "count_not_in_future"
    PERCENT_NOT_IN_FUTURE = "percent_not_in_future"
    COUNT_DATE_NOT_IN_FUTURE = "count_date_not_in_future"
    PERCENT_DATE_NOT_IN_FUTURE = "percent_date_not_in_future"

    # -- Geolocation Information
    COUNT_LATITUDE = "count_latitude"
    PERCENT_LATITUDE = "percent_latitude"
    COUNT_LONGITUDE = "count_longitude"
    PERCENT_LONGITUDE = "percent_longitude"

    # CROSS Validation
    COMPARE_COUNT_ROWS = "compare_count_rows"

    # Failed rows
    FAILED_ROWS = "failed_rows"


@dataclass
class ValidationInfo:
    name: str
    identity: str
    data_source_name: str
    dataset: str
    validation_function: ValidationFunction
    value: Union[int, float]
    timestamp: datetime
    field: Optional[str] = None
    is_valid: Optional[bool] = None
    reason: Optional[str] = None
    tags: Dict[str, str] = None
