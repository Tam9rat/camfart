UPDATE [Stamperia] SET [Data_valid] = CURRENT_TIMESTAMP
WHERE [Flag] = 1 AND [Data_valid] IS NULL
