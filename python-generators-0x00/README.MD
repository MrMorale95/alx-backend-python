# Python Generators (0x00)

A technical exploration of Python generators for efficient data processing and streaming from MySQL databases. This project demonstrates scalable techniques for handling large datasets with optimal memory usage.

## Key Features

- **Lazy Loading**: On-demand data streaming to minimize memory footprint
- **Batch Processing**: Efficient handling of data in configurable chunks
- **Pagination Simulation**: Implementation of lazy pagination for database queries
- **Streaming Aggregates**: Memory-efficient computation of aggregate values (e.g., averages)

## Implementation Goals

1. MySQL database configuration and population with sample user data
2. Row-by-row data streaming using generator functions
3. Optimized batch processing of user records
4. Paginated query simulation through lazy loading techniques
5. Streaming computation of aggregate metrics

## Technology Stack

- Python 3
- MySQL Database
- mysql-connector-python driver
- CSV format for initial data seeding