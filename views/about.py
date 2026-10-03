"""Page 5 - About."""
from utils import data
from utils.styles import card, grid, md, page_header, section


def node(text, color):
    return f'<div class="pg-node" style="background:{color}">{text}</div>'


def render():
    page_header("About PhishGuard AI", "Phishing, the dataset, the neural network and the Data Structures behind it.")
    arrow = '<div class="pg-arrow">-&gt;</div>'

    section("What is phishing?")
    md(card("Fake websites that steal your data",
            "Phishing is a cyber attack where a fake website imitates a trusted one (a bank, a shop, a login page) "
            "to trick people into typing passwords, card numbers or personal details. Blacklists only know sites that "
            "were already reported, so a model that learns suspicious patterns can catch new ones.", "", "red"))

    section("Dataset")
    stats = data.dataset_stats()
    size = (f"<b>{stats['rows']:,}</b> websites ({stats['phishing']:,} phishing, {stats['legit']:,} legitimate). "
            if stats else "")
    md(card("Phishing Dataset for Machine Learning (Kaggle)",
            f"File <span class='pg-code'>dataset/phishing.csv</span> (Phishing_Legitimate_full.csv). {size}"
            "Each row is a website described by numeric features and a <span class='pg-code'>CLASS_LABEL</span>. "
            "The ANN uses 12 of them: NumDots, SubdomainLevel, PathLevel, UrlLength, NumDash, AtSymbol, NumNumericChars, "
            "NoHttps, IpAddress, NumSensitiveWords, HostnameLength, PctExtHyperlinks.", "", "purple"))

    section("ANN architecture")
    md('<div class="pg-card"><div class="pg-flow">'
       + node("Input<br>12 features", "#334E7A") + arrow + node("Dense 16<br>ReLU", "#2563EB") + arrow
       + node("Dense 8<br>ReLU", "#2563EB") + arrow + node("Output 1<br>Sigmoid", "#10B981") + "</div>"
       '<div class="pg-card-body">Adam optimizer, binary cross-entropy, 25 epochs, batch size 32, 80:20 split, '
       "StandardScaler. The sigmoid output is the probability of <i>Legitimate</i>; risk score = (1 minus p) x 100 "
       "(0-30 Low, 31-70 Medium, 71-100 High). Security score = 100 minus risk score.</div></div>")

    section("Where the Data Structures are used")
    md(grid([
        card("Arrays / lists", "The <span class='pg-code'>FEATURES</span> list and the 12-value feature vector that goes through the scaler into the ANN; NumPy arrays hold the scaled data.", "", "blue"),
        card("Strings", "URL analysis in <span class='pg-code'>utils/parser.py</span> and <span class='pg-code'>feature_extractor.py</span>: counting dots, dashes, digits, '@', sensitive words and splitting host/path.", "", "green"),
        card("Hash maps / sets", "<span class='pg-code'>features_dict</span> passed to <span class='pg-code'>predict_website()</span>, <span class='pg-code'>FEATURE_INFO</span> rules, and the <span class='pg-code'>SHORTENERS</span> hash set for O(1) lookups.", "", "purple"),
        card("CSV (tabular storage)", "<span class='pg-code'>dataset/phishing.csv</span> is loaded into a DataFrame; metrics are stored in <span class='pg-code'>assets/metrics.json</span>.", "", "amber"),
    ]))

    section("Limitations")
    md(card("Read this before trusting a result",
            "By default the scanner analyses only the URL text and never downloads anything, so the external-link "
            "feature uses a neutral default. The URL Scanner page has an optional checkbox to fetch the live page "
            "and measure that feature for real - useful for accuracy, but it does mean your computer makes a real "
            "network request to the address, which only makes sense for sites you're comfortable connecting to. "
            "Either way, treat the result as decision support, not a guarantee.", "", "amber"))
