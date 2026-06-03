\# Mutual Fund Project - Data Dictionary



\## 1. dim\_fund (Dimension Table)

\* `amfi\_code` (INTEGER, PK): Unique 6-digit identification code provided by AMFI India.

\* `fund\_house` (TEXT): The Asset Management Company organizing the fund portfolio.

\* `scheme\_name` (TEXT): Complete official designation of the mutual fund scheme option.

\* `category` (TEXT): Primary asset classification group (e.g., Equity, Debt).

\* `sub\_category` (TEXT): Granular asset target focus strategy (e.g., Large Cap, Mid Cap).

\* `plan` (TEXT): Growth choice structure categorization (Direct or Regular Plan alternatives).

\* `fund\_manager` (TEXT): Registered chief investment expert supervising portfolio executions.



\## 2. fact\_nav (Fact Table)

\* `nav\_id` (INTEGER, PK AutoIncrement): System-generated structural line key tracking element.

\* `amfi\_code` (INTEGER, FK): Relational link code pointing to target fund attributes in `dim\_fund`.

\* `date` (TEXT, FK): Specific transaction index date pointing to `dim\_date`.

\* `nav` (REAL): Net Asset Value price score metric representing share unit value on that day.

