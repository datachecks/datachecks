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

import datetime
import json
from abc import ABC
from typing import Optional, Tuple, Union

from loguru import logger

from datachecks.core.common.models.metric import MetricsType, MetricValue
from datachecks.core.common.models.validation import ConditionType
from datachecks.core.datasource.base import DataSource
from datachecks.core.datasource.search_datasource import SearchIndexDataSource
from datachecks.core.datasource.sql_datasource import SQLDataSource


class MetricIdentity:
    @staticmethod
    def generate_identity(
        metric_type: MetricsType,
        metric_name: str,
        data_source: DataSource = None,
        expression: str = None,
        index_name: str = None,
        table_name: str = None,
        field_name: str = None,
    ):
        """
        Generate a unique identifier for a metric
        """

        identifiers = []

        if data_source is not None:
            identifiers.append(data_source.data_source_name)
        if index_name:
            identifiers.append(index_name)
        elif table_name:
            identifiers.append(table_name)
        if field_name:
            identifiers.append(field_name)

        identifiers.append(metric_type.value)
        if metric_name:
            identifiers.append(metric_name)
        return ".".join([str(p) for p in identifiers])


class Metric(ABC):
    """
    Metric is a class that represents a metric that is generated by a data source.
    """

    def __init__(
        self,
        name: str,
        metric_type: MetricsType,
        data_source: DataSource = None,
        expression: str = None,
        **kwargs,
    ):
        if metric_type == MetricsType.COMBINED:
            if expression is None:
                raise ValueError("Please give an expression for combined metric")
        else:
            if "index_name" in kwargs and "table_name" in kwargs:
                if (
                    kwargs["index_name"] is not None
                    and kwargs["table_name"] is not None
                ):
                    raise ValueError(
                        "Please give a value for table_name or index_name (but not both)"
                    )
            if "index_name" not in kwargs and "table_name" not in kwargs:
                raise ValueError("Please give a value for table_name or index_name")

            self.index_name, self.table_name = None, None
            if "index_name" in kwargs:
                self.index_name = kwargs["index_name"]
            if "table_name" in kwargs:
                self.table_name = kwargs["table_name"]

        self.name: str = name
        self.metric_type = metric_type
        self.data_source = data_source
        self.expression = expression
        self.filter_query = None
        if "filters" in kwargs and kwargs["filters"] is not None:
            filters = kwargs["filters"]
            if hasattr(filters, "where"):
                if isinstance(data_source, SearchIndexDataSource):
                    self.filter_query = json.loads(filters.where)
                elif isinstance(data_source, SQLDataSource):
                    self.filter_query = filters.where
        self.validation = None
        if "validation" in kwargs and kwargs["validation"] is not None:
            self.validation = kwargs["validation"]

    def get_metric_identity(self):
        MetricIdentity.generate_identity(
            metric_type=self.metric_type,
            metric_name=self.name,
            data_source=self.data_source,
            expression=self.expression,
        )

    def _generate_metric_value(self, **kwargs) -> float:
        pass

    def get_metric_value(self, **kwargs) -> Union[MetricValue, None]:
        try:
            metric_value = self._generate_metric_value(**kwargs)
            tags = {
                "metric_name": self.name,
            }
            if self.metric_type.value == MetricsType.COMBINED.value:
                value = MetricValue(
                    identity=self.get_metric_identity(),
                    metric_type=self.metric_type.value,
                    value=metric_value,
                    expression=self.expression,
                    timestamp=datetime.datetime.utcnow().isoformat(),
                    tags=tags,
                )
            else:
                value = MetricValue(
                    identity=self.get_metric_identity(),
                    metric_type=self.metric_type.value,
                    value=metric_value,
                    timestamp=datetime.datetime.utcnow().isoformat(),
                    data_source=self.data_source.data_source_name,
                    expression=self.expression,
                    tags=tags,
                )
            if self.validation is not None and self.validation.threshold is not None:
                value.is_valid, value.reason = self.validate_metric(metric_value)

            if (
                "index_name" in self.__dict__
                and self.__dict__["index_name"] is not None
            ):
                value.index_name = self.__dict__["index_name"]
            elif (
                "table_name" in self.__dict__
                and self.__dict__["table_name"] is not None
            ):
                value.table_name = self.__dict__["table_name"]

            if (
                "field_name" in self.__dict__
                and self.__dict__["field_name"] is not None
            ):
                value.field_name = self.__dict__["field_name"]

            return value
        except Exception as e:
            logger.error(f"Failed to generate metric {self.name}: {str(e)}")
            return None

    def validate_metric(self, metric_value) -> Tuple[bool, Optional[str]]:
        for operator, value in self.validation.threshold.__dict__.items():
            if value is not None:
                if ConditionType.GTE == operator:
                    if metric_value < value:
                        return (
                            False,
                            f"Less than threshold of {value}",
                        )
                elif ConditionType.LTE == operator:
                    if metric_value > value:
                        return (
                            False,
                            f"Greater than threshold of {value}",
                        )
                elif ConditionType.GT == operator:
                    if metric_value <= value:
                        return (
                            False,
                            f"Less than or equal to threshold of {value}",
                        )
                elif ConditionType.LT == operator:
                    if metric_value >= value:
                        return (
                            False,
                            f"Greater than or equal to threshold of {value}",
                        )
                elif ConditionType.EQ == operator:
                    if metric_value != value:
                        return (
                            False,
                            f"Not equal to {value}",
                        )
        return True, None


class FieldMetrics(Metric, ABC):
    def __init__(
        self,
        name: str,
        metric_type: MetricsType,
        data_source: Optional[DataSource] = None,
        expression: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            data_source=data_source,
            expression=expression,
            metric_type=metric_type,
            **kwargs,
        )
        if "field_name" in kwargs:
            self.field_name = kwargs["field_name"]

    @property
    def get_field_name(self):
        return self.field_name
