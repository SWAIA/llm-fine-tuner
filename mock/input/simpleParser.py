database_sql_content = ""


# Simplified custom parser to extract table names and column names
def simplified_sql_parser(sql_content):
    tables = []

    # Splitting the SQL content into individual statements
    sql_statements = sql_content.split(";")

    # Iterating through each statement to identify CREATE TABLE statements
    for statement in sql_statements:
        statement = statement.strip()
        if statement.lower().startswith("create table"):
            table_details = {"name": None, "columns": []}

            # Extracting the table name
            table_name_part = statement.split("(")[0].strip()
            table_details["name"] = table_name_part.split()[-1]

            # Extracting the columns (without considering data types and constraints)
            columns_part = statement.split("(", 1)[1].rsplit(")", 1)[0].strip()
            columns_definitions = [
                col.strip().split()[0] for col in columns_part.split(",") if col.strip()
            ]

            table_details["columns"] = columns_definitions

            tables.append(table_details)

    return tables


# Parsing the database.sql content using the simplified custom parser
simplified_parsed_tables = simplified_sql_parser(database_sql_content)
simplified_parsed_tables

# Output:
""" [{'name': 'public.profile',
  'columns': ['id',
   'username',
   'email',
   'profile_image',
   'created_at',
   ')',
   'title',
   'subtitle',
   'artist_id',
   'file_id',
   'region_id',
   'style',
   'description',
   'price',
   'quantity',
   'availability',
   "'Not",
   "'Sold",
   'shipping_info',
   'created_at',
   'user_profile_id',
   'business_name',
   'first_name',
   'last_name',
   'bio',
   '--',
   'phone',
   "15}$')",
   '--',
   'city',
   'state_province',
   'zip_code',
   'profile_image',
   'avatar',
   'store_name',
   'store_description',
   'store_banner',
   'user_profile_id',
   '--',
   'subtitle',
   'description',
   'image',
   'status',
   "'public'",
   "'private'))",
   'updated_at']},
 {'name': 'public.collection_item',
  'columns': ['id',
   'collection_id',
   '--',
   'item_id',
   'CONSTRAINT',
   'item_id)']}] """
