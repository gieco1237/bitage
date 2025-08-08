# Bitage - Crypto Investment Manager

Bitage is a desktop application built with Python and Tkinter that helps you manage and automate cryptocurrency investment strategies. It provides tools for two distinct plan types: **DinamicDCA** for advanced, rule-based investing around an asset's All-Time High (ATH), and **Cryptopips** for simpler, price-target-based strategies.

The application fetches real-time market data, calculates key performance indicators, and provides actionable recommendations based on your predefined rules.

---

## ✨ Features

-   **Dual Strategy Support**: Manage both `DinamicDCA` and `Cryptopips` plans from a single interface.
-   **Real-Time Data**: Integrates with the Yahoo Finance API (`yfinance`) to fetch live cryptocurrency prices and historical data.
-   **DinamicDCA Plans**:
    -   Define buy/sell rules based on percentages of a manual or real-time All-Time High (ATH).
    -   Calculates key metrics like "Current Drop from ATH" and "Maximum Drop from ATH".
    -   Provides clear buy/sell action recommendations.
-   **Cryptopips Plans**:
    -   Set a simple buy price and define sell targets based on price multipliers.
    -   Track profit/loss in real-time.
-   **Interactive Controls**: Dynamically enable or disable individual sell-side rules for any plan with a single click, allowing for flexible strategy adjustments.
-   **Persistent Storage**: All your investment plans are securely saved locally in an SQLite database.
-   **Intuitive GUI**: A clean and user-friendly graphical interface built with Tkinter.

---

## 🛠️ Technologies Used

-   **Backend**: Python
-   **GUI**: Tkinter (Python's standard GUI package)
-   **Data**: yfinance (Yahoo Finance API)
-   **Database**: SQLite 3

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

-   Python 3.6+

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/AngelDG9/bitage.git
    cd bitage
    ```

2.  **Create a virtual environment (recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```sh
    python bitage.py
    ```
    (Assuming your main script is named `bitage.py`)

---

## 📖 How to Use

1.  **Select Plan Type**: Choose between `DinamicDCA` and `Cryptopips` at the top-left.
2.  **Manage Plans**: Use the `Add Plan`, `Edit Plan`, and `Delete Plan` buttons to manage your strategies.
3.  **View Details**: Click on any plan in the list to see its details, real-time analysis, and recommended actions on the right-hand panel.
4.  **Toggle Sell Rules**: In the "Sell Plan" section of the details panel, click the checkbox next to any rule to enable or disable it. The change is saved automatically and reflected in the "Recommended Actions".

---

## 📄 License

This project is licensed under the MIT License.
