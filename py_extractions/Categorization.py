import pandas as pd

# Load Excel file (starting from correct header row)
input_file = "category_extraction.xlsx"
df = pd.read_excel(input_file, header=1)

# Rename columns for easier reference
df.columns = ['No', 'people', 'designation', 'company', 'category', 'country', 'linkedIn', 'twitter', 'feature-1', 'feature-2',
              'category-1', 'category-2', 'category-3', 'excerpt']

# # Drop rows missing both company and excerpt
# df = df.dropna(subset=['company', 'excerpt'])

# Define a helper function to infer categories and features
def infer_categories_and_features(company, excerpt):
    company = str(company).lower() if pd.notna(company) else ""
    excerpt = str(excerpt).lower() if pd.notna(excerpt) else ""

    categories = []
    features = []

    category_keywords = {
        "finance": ["finance", "fintech", "financial", "investment", "trading"],
        "education": ["edtech", "learning", "education", "students", "schools"],
        "healthcare": ["health", "medical", "healthcare", "clinical", "hospitals"],
        "mobility": ["automotive", "vehicle", "mobility", "transport", "fleet"],
        "agriculture": ["farm", "agri", "crop", "agriculture", "soil"],
        "computer vision": ["image", "vision", "camera", "object detection"],
        "nlp": ["language", "nlp", "text", "conversational", "chatbot"],
        "cybersecurity": ["cyber", "security", "breach", "threat"],
        "iot": ["iot", "sensor", "device", "connected"],
        "cloud": ["cloud", "infrastructure", "saas"],
        "ai/ml": ["machine learning", "ai", "artificial intelligence", "deep learning", "neural network", "ml"],
        "analytics": ["analytics", "data-driven", "business intelligence"],
        "robotics": ["robotics", "robot", "automation"],
        "retail": ["retail", "ecommerce", "shopping", "merchandise"],
        "legal": ["law", "legal", "contract", "compliance"],
        "academic": ["professor", "researcher", "phd", "ph.d", 'Dr', "doctorate", "faculty", "postdoc"]
    }

    # Check for category matches
    for category, keywords in category_keywords.items():
        if any(kw in company or kw in excerpt for kw in keywords):
            categories.append(category.title())

        # Features
    if "machine learning" in excerpt or "ml" in excerpt:
        features.append("Machine Learning")
    if "deep learning" in excerpt or "neural network" in excerpt:
        features.append("Deep Learning")
    if "data" in excerpt or "analytics" in excerpt or "insight" in excerpt:
        features.append("Data Analytics")
    if "data engineering" in excerpt or "pipelines" in excerpt:
        features.append("Data Engineering")
    if "visualization" in excerpt or "dashboards" in excerpt:
        features.append("Visualization")
    if "business intelligence" in excerpt or "bi tools" in excerpt:
        features.append("Business Intelligence")
    if "automation" in excerpt or "optimization" in excerpt:
        features.append("Automation")
    if "iot" in excerpt or "sensor" in excerpt or "edge device" in excerpt:
        features.append("IoT")
    if "robot" in excerpt or "robotics" in excerpt:
        features.append("Robotics")
    if "platform" in excerpt or "ecosystem" in excerpt:
        features.append("Platform")
    if "cloud" in excerpt or "infrastructure" in excerpt:
        features.append("Cloud")
    if "api" in excerpt or "integration" in excerpt:
        features.append("APIs")
    if "saas" in excerpt or "subscription" in excerpt:
        features.append("SaaS")
    if "security" in excerpt or "cyber" in excerpt or "threat" in excerpt:
        features.append("Cybersecurity")
    if "devops" in excerpt or "ci/cd" in excerpt:
        features.append("DevOps")
    if "nlp" in excerpt or "natural language" in excerpt:
        features.append("Natural Language Processing")
    if "text" in excerpt or "chatbot" in excerpt or "language model" in excerpt:
        features.append("Text Intelligence")
    if "speech" in excerpt or "voice" in excerpt:
        features.append("Speech Processing")
    if "image" in excerpt or "vision" in excerpt or "object detection" in excerpt:
        features.append("Computer Vision")
    if "professor" in excerpt or "phd" in excerpt or "researcher" in excerpt or "postdoc" in excerpt:
        features.append("PhD")

    features = features[:2]
    categories = categories[:3]

    # Ensure 'Others' is used as fallback if no category was found
    primary_category = categories[0] if categories else "Others"

    # # If no category found, return 'Misc' as default category
    # primary_category = categories[0] if categories else "Misc"

    return pd.Series([
        primary_category,
        features[0] if len(features) > 0 else "",
        features[1] if len(features) > 1 else "",
        categories[0] if len(categories) > 0 else "",
        categories[1] if len(categories) > 1 else "",
        categories[2] if len(categories) > 2 else "",
    ])

# Apply function to each row
df[['category', 'feature-1', 'feature-2', 'category-1', 'category-2', 'category-3']] = df.apply(
    lambda row: infer_categories_and_features(row['company'], row['excerpt']),
    axis=1
)

# Save updated data to Excel
output_file = "filled_categories.xlsx"
df.to_excel(output_file, index=False)
print(f"✅ Categorized data saved to: {output_file}")