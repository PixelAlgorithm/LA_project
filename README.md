# Economic Ripple Simulator

**A Linear Algebra Course Project**

An interactive, web-based Leontief Input-Output Model simulator built using pure Python via **PyScript**. This tool allows you to input custom matrix coefficients and demand for various economic sectors. It solves the Leontief equation `X = (I - A)^-1 D` entirely inside the browser using Linear Algebra matrices, demonstrating the hidden chain reactions (ripple effects) across industries.

## Contributors

| SRN | Name |
| :--- | :--- |
| PES2UG24CS910 | Prajwal M |
| PES2UG24CS150 | Deepthi V |
| PES2UG24CS917 | R.P Pranav |
| PES2UG24CS159 | Dimpal N |

---

## 🚀 How to Host This on GitHub Pages (Free & Easy)

Since all the Python logic runs in the browser, deploying this app is incredibly straightforward.

1. Go to this repository on GitHub.
2. Click on the **Settings** tab.
3. On the left sidebar, click on **Pages**.
4. Under "Build and deployment", set the **Source** to `Deploy from a branch`.
5. Under "Branch", select `main` (or `master`) and select the `/ (root)` folder.
6. Click **Save**.

After a minute or two, GitHub will provide you with a live URL. Anyone can visit that link, the browser will download PyScript, and the app will run perfectly!

## Run Locally
To test it on your local machine, open a terminal in this directory and start a simple web server:
```bash
python3 -m http.server 8080
```
Then visit `http://localhost:8080`!
