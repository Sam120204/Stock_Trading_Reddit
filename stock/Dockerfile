# Use Amazon Linux 2 as the base image
FROM amazonlinux:2

# Install necessary packages
RUN yum install -y python3 python3-devel gcc postgresql-devel zip

# Upgrade pip and install dependencies
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip
RUN pip3 install psycopg2-binary yfinance

# Create directories for Lambda function and package
RUN mkdir -p /lambda_function /package /mnt/output

# Set working directory
WORKDIR /lambda_function

# Copy Lambda function script
COPY lambda_fetch_store_stock_prices.py /lambda_function/

# Install dependencies in the package directory
RUN pip3 install psycopg2-binary yfinance -t /package

# Move Lambda function script to the package directory
RUN cp -r /lambda_function/* /package/

# Create a zip file of the package
WORKDIR /package
RUN zip -r /mnt/output/lambda_function.zip .
