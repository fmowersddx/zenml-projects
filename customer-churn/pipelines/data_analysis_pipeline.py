from zenml.pipelines import pipeline


@pipeline
def data_analysis_pipeline(ingest_data, data_splitter):
    """Pipeline for analyzing data.

    Args:
        ingest_data  : Ingest data from the data source.
        data_splitter: Splits the data into train and test data.
    """
    customer_churn_df = ingest_data()
    train, test = data_splitter(customer_churn_df)
