# Economic Ripple Simulator

**A Linear Algebra Course Project**

An interactive, web-based Leontief Input-Output Model simulator built using Python (via **PyScript**) and WebAssembly to solve complex linear algebra matrices completely in the browser.

## The Project (What It Does)

In a real economy, industries do not operate in isolation. When consumers demand a product (like cars), the automobile sector must purchase steel, rubber, and electricity. In turn, the steel industry must purchase coal and more electricity. This creates a cascading **ripple effect** throughout the entire supply chain. 

This project simulates exactly that behavior using the **Leontief Input-Output Model**, a famous application of Linear Algebra in macroeconomics. 

### How It Works using Linear Algebra:
1. **Inputs:** The user defines an `n × n` Input-Output coefficient matrix (`A`), where each column represents the requirements of an industry. The user also defines a final consumer demand vector (`D`).
2. **The Leontief Equation:** To find the total output required by every sector (`X`), the simulator solves the classic equation:
   `X = (I - A)^-1 * D`
3. **The Leontief Inverse (`(I - A)^-1`):** The program calculates the inverse of the identity matrix minus the coefficient matrix. This magical inverse matrix maps out the total integrated supply chain footprint.
4. **Output:** The application outputs the required production from every sector and translates the complex Inverse Matrix into a simple, readable "story" of how `$1` of demand in one sector ripples across the others.

By applying `numpy` matrix inversions via PyScript natively in the browser, the app translates complex structural economics into an intuitive, visual web interface.

## Contributors

| SRN | Name |
| :--- | :--- |
| PES2UG24CS910 | Prajwal M |
| PES2UG24CS150 | Deepthi V |
| PES2UG24CS917 | R.P Pranav |
| PES2UG24CS159 | Dimpal N |

---

## Run Locally
To test it on your local machine, open a terminal in this directory and start a simple web server:
```bash
python3 -m http.server 8080
```
Then visit `http://localhost:8080` in your web browser!
