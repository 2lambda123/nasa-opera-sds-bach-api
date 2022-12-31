import json
from unittest.mock import MagicMock

import pandas
from pandas.testing import assert_frame_equal
from pytest_mock import MockerFixture

from accountability_api.api_utils.reporting.production_time_detailed_report import ProductionTimeDetailedReport


def test_generate_report_json_empty(test_client, mocker: MockerFixture):
    # ARRANGE
    mocker.patch("accountability_api.api_utils.query.get_docs", MagicMock())
    report = ProductionTimeDetailedReport(title="Test Report", start_date="1970-01-01", end_date="1970-01-01", timestamp="1970-01-01")

    # ACT
    json_report = report.generate_report("application/json")

    # ASSERT
    assert json.loads(json_report)["payload"] == []


def test_generate_report_csv_empty(test_client, mocker: MockerFixture):
    # ARRANGE
    mocker.patch("accountability_api.api_utils.query.get_docs", MagicMock())
    report = ProductionTimeDetailedReport(title="Test Report", start_date="1970-01-01", end_date="1970-01-01", timestamp="1970-01-01")

    # ACT
    csv_report = report.generate_report("text/csv")

    # ASSERT
    with open(csv_report.name) as fp:
        assert fp.read() == (
            "Title: OPERA Production Time Log\n"
            "Date of Report: 1970-01-01T00:00:00Z\n"
            "Period of Coverage (AcquisitionTime): 1970-01-01T00:00:00Z-1970-01-01T00:00:00Z\n"
            "\n"
        )


def test_to_report_df_empty_db(test_client):
    # ARRANGE
    report = ProductionTimeDetailedReport(title="Test Report", start_date="1970-01-01", end_date="1970-01-01", timestamp="1970-01-01")

    # ACT
    report_df = report.to_report_df(product_docs=[], report_type="detailed")

    # ASSERT
    assert_frame_equal(report_df, pandas.DataFrame())


def test_to_report_df_no_reportable_products(test_client):
    # ARRANGE
    report = ProductionTimeDetailedReport(title="Test Report", start_date="1970-01-01", end_date="1970-01-01", timestamp="1970-01-01")

    # ACT
    report_df = report.to_report_df(product_docs=[{}], report_type="detailed")

    # ASSERT
    assert_frame_equal(report_df, pandas.DataFrame())


def test_to_report_df_reportable_products_detailed(test_client):
    # ARRANGE
    report = ProductionTimeDetailedReport(title="Test Report", start_date="1970-01-01", end_date="1970-01-01", timestamp="1970-01-01")

    # ACT
    report_df = report.to_report_df(
        product_docs=[
            {
                "daac_CNM_S_timestamp": "1970-01-01",
                "metadata": {
                    "ProductReceivedTime": "1970-01-01",
                    "FileName": "dummy_opera_product_name",
                    "ProductType": "dummy_opera_product_short_name"
                }
            }
        ],
        report_type="detailed"
    )

    # ASSERT
    first_row = report_df.to_dict(orient="records")[0]
    assert first_row["opera_product_name"] == "dummy_opera_product_name"
    assert first_row["opera_product_short_name"] == "dummy_opera_product_short_name"
    assert first_row["production_time"] == "00:00:00"


def test_to_report_df_reportable_products_summary(test_client):
    # ARRANGE
    report = ProductionTimeDetailedReport(title="Test Report", start_date="1970-01-01", end_date="1970-01-01", timestamp="1970-01-01")

    # ACT
    report_df = report.to_report_df(
        product_docs=[
            {
                "daac_CNM_S_timestamp": "1970-01-01T01:00:00",
                "metadata": {
                    "ProductReceivedTime": "1970-01-01",
                    "FileName": "dummy_opera_product_name",
                    "ProductType": "dummy_opera_product_short_name"
                }
            },
            {
                "daac_CNM_S_timestamp": "1970-01-01T02:00:00",
                "metadata": {
                    "ProductReceivedTime": "1970-01-01",
                    "FileName": "dummy_opera_product_name",
                    "ProductType": "dummy_opera_product_short_name"
                }
            },
            {
                "daac_CNM_S_timestamp": "1970-01-01T03:00:00",
                "metadata": {
                    "ProductReceivedTime": "1970-01-01",
                    "FileName": "dummy_opera_product_name",
                    "ProductType": "dummy_opera_product_short_name"
                }
            }
        ],
        report_type="summary"
    )

    # ASSERT
    first_row = report_df.to_dict(orient="records")[0]
    assert first_row["opera_product_short_name"] == "dummy_opera_product_short_name"
    assert first_row["production_time_count"] == 3
    assert first_row["production_time_min"] == "01:00:00"
    assert first_row["production_time_max"] == "03:00:00"
    assert first_row["production_time_mean"] == "02:00:00"
    assert first_row["production_time_median"] == "02:00:00"
