import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import re

# Initialize the Dash app with Bootstrap for better styling
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Read the Excel file
df = pd.read_excel('IndiaAI_Complete_Updated.xlsx', sheet_name='Sheet1')

# Clean and prepare the data
df = df.dropna(subset=['category', 'company', 'people'])  # Remove rows with missing essential data

# Create people_designation with line breaks
df['people_designation'] = df['people'] + '<br>(' + df['designation'].fillna('') + ')'

# Create the sunburst plot with larger size
fig = px.sunburst(
    df,
    path=['category', 'company'], #'people_designation'
    maxdepth=2,  # Show up to 2 levels from root
    branchvalues='total',
    height=700,  # Make plot taller
    # width=1200,   # Make plot wider
    #hover_data={col: False for col in ['category', 'company']}  # people_designation. -- Disable hover
    hover_data={}
)

# Customize layout
fig.update_layout(
    margin=dict(t=0, l=0, r=0, b=0),
    sunburstcolorway=px.colors.qualitative.Pastel,
    font=dict(size=14)  # Increase font size for better readability
)

fig.update_traces(hovertemplate=None, hoverinfo='skip')

# Update the app.layout section
# Update the app.layout section
app.layout = dbc.Container([
    # Top row: Sunburst and Company Info
    dbc.Row([
        # Sunburst plot (left)
        dbc.Col([
            dcc.Graph(
                id='sunburst-chart',
                figure=fig,
                config={
                    'displayModeBar': True,
                    'scrollZoom': True,  # Enable zoom
                    'displaylogo': False,
                    'modeBarButtonsToAdd': ['resetScale2d', 'toImage']
                },
                style={'height': '70vh', 'width': '100%'}  # Responsive sizing
            )
        ], md=7, className="pr-2"),  # Right padding for buffer
        
        # Company info (right)
        dbc.Col([
            html.Div(id='company-details', style={
                'height': '70vh',
                'overflow-y': 'auto',
                'padding': '10px'
            })
        ], md=5, className="pl-2")  # Left padding for buffer
    ], className="mb-4"),
    
    # Buffer space between sections
    dbc.Row(html.Div(style={'height': '10px'})),  # Buffer space
    
    # People info (bottom)
    dbc.Row([
        dbc.Col([
            html.Div(id='people-details', style={
                'margin-top': '10px',
                'padding': '15px',
                'background-color': '#f8f9fa',
                'border-radius': '8px'
            })
        ], width=12)
    ])
], fluid=True, style={'padding': '20px'})

# Function to validate URLs
def is_valid_url(url):
    if not isinstance(url, str) or url.strip() == "":
        return False
    return re.match(r'^https?://', url) is not None

# Modified create_company_card function for compact display
def create_company_card(company_data):
    """Create a compact card with company information for right panel"""
    # Create location information
    location_info = []
    if pd.notna(company_data.get('location')):
        location_info.append(company_data['location'])
    if pd.notna(company_data.get('state')):
        location_info.append(company_data['state'])
    if pd.notna(company_data.get('company_country')):
        location_info.append(company_data['company_country'])
    location_text = ", ".join(location_info) if location_info else "Location not available"
    
    # Create category information
    category_info = []
    if pd.notna(company_data.get('company_head_category')):
        category_info.append(company_data['company_head_category'])
    if pd.notna(company_data.get('company_categories')):
        category_info.append(company_data['company_categories'])
    category_text = " | ".join(category_info) if category_info else "Category not available"
    
    # Create social media links
    website_element = html.P("🌐 Website: Not available", className="card-text mb-1")
    if pd.notna(company_data.get('website')) and is_valid_url(company_data['website']):
        website_element = html.P([
            "🌐 Website: ",
            html.A("Link", href=company_data['website'], target="_blank", className="text-primary")
        ], className="card-text mb-1")
    
    linkedin_element = html.P("🔗 LinkedIn: Not available", className="card-text mb-1")
    if pd.notna(company_data.get('company_linkedIn')) and is_valid_url(company_data['company_linkedIn']):
        linkedin_element = html.P([
            "🔗 LinkedIn: ",
            html.A("Link", href=company_data['company_linkedIn'], target="_blank", className="text-primary")
        ], className="card-text mb-1")
    
    twitter_element = html.P("🐦 Twitter: Not available", className="card-text mb-1")
    if pd.notna(company_data.get('company_twitter')) and is_valid_url(company_data['company_twitter']):
        twitter_element = html.P([
            "🐦 Twitter: ",
            html.A("Link", href=company_data['company_twitter'], target="_blank", className="text-info")
        ], className="card-text mb-1")
    
    # Create company image
    img_element = html.Div(className="text-center")
    if 'company_image_url' in company_data and pd.notna(company_data['company_image_url']) and is_valid_url(company_data['company_image_url']):
        img_element = html.Div(
            html.Img(
                src=company_data['company_image_url'],
                style={
                    'height': '120px',
                    'max-width': '100%',
                    'object-fit': 'contain',
                    'border': '2px solid #ddd'
                }
            ),
            className="text-center mb-2"
        )
    elif 'company_image_url' in company_data and pd.notna(company_data['company_image_url']):
        img_element = html.P("⚠️ Invalid image URL", className="text-center text-muted mb-2")
    else:
        img_element = html.P("📷 No image", className="text-center text-muted mb-2")
    
    # Create description (short_excerpt + highlights)
    description = []
    if pd.notna(company_data.get('short_excerpt')):
        # Truncate excerpt for compact display
        excerpt = company_data['short_excerpt']
        if len(excerpt) > 200:
            excerpt = excerpt[:200] + "..."
        description.append(html.P(excerpt, className="card-text small"))
    if pd.notna(company_data.get('highlights')):
        # Truncate highlights for compact display
        highlights = company_data['highlights']
        if len(highlights) > 200:
            highlights = highlights[:200] + "..."
        description.append(html.P(highlights, className="card-text small mt-2"))
    if not description:
        description = html.P("No description available", className="card-text text-muted small")
    
    # Create tags and features
    tags_element = html.P("🏷️ Tags: Not available", className="card-text small mb-1")
    if pd.notna(company_data.get('company_tags')):
        tags_element = html.P(f"🏷️ Tags: {company_data['company_tags']}", className="card-text small mb-1")
    
    features_element = html.P("✨ Features: Not available", className="card-text small mb-1")
    if pd.notna(company_data.get('company_feature')):
        features_element = html.P(f"✨ Features: {company_data['company_feature']}", className="card-text small mb-1")
    
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H4(f"🏢 {company_data['company']}", className="mb-0"),
                className="bg-light py-2"
            ),
            dbc.CardBody(
                [
                    dbc.Row([
                        # Left column with text info
                        dbc.Col([
                            html.P(f"📍 {location_text}", className="card-text small mb-1"),
                            html.P(f"📂 {category_text}", className="card-text small mb-1"),
                            tags_element,
                            features_element,
                            html.Div([
                                website_element,
                                linkedin_element,
                                twitter_element
                            ], className="mt-2")
                        ], md=7),
                        # Right column with image
                        dbc.Col([
                            img_element
                        ], md=5)
                    ]),
                    html.Hr(className="my-2"),
                    *(description if isinstance(description, list) else [description])
                ]
            ),
        ],
        className="shadow-sm",
        style={
            "border-radius": "8px",
            "border": "1px solid #eee",
            'border-left': '1px solid #eee',
            'padding-left': '15px'
        }
    )

# Callback to display company and people details
@app.callback(
    [Output('company-details', 'children'),
     Output('people-details', 'children')],
    [Input('sunburst-chart', 'clickData')]
)
def display_details(click_data):
    if click_data is None:
        return html.Div(), html.Div()
    
    # Extract current path from clickData
    point = click_data['points'][0]
    current_path = point.get('id', '')
    path_components = current_path.split('/')
    
    # Show details when at company level (level-1)
    if len(path_components) == 2:  # Exactly 2 components: [category, company]
        company = path_components[1]
        
        # Get first row of company data
        company_rows = df[df['company'] == company]
        company_row = company_rows.iloc[0] if not company_rows.empty else None
        
        # Create company details section
        company_details = html.Div()
        if company_row is not None:
            company_details = create_company_card(company_row)
        
        # Create people details section
        people_details = html.Div()
        if not company_rows.empty:
            cards = []
            for _, row in company_rows.iterrows():
                # ... (keep your existing person card creation code)
                # Create LinkedIn link if available
                linkedin_element = html.P("🔗 LinkedIn: Not available", className="card-text")
                if pd.notna(row['linkedIn']) and is_valid_url(row['linkedIn']):
                    linkedin_element = html.P([
                        "🔗 LinkedIn: ",
                        html.A(row['linkedIn'], href=row['linkedIn'], target="_blank", className="text-primary")
                    ], className="card-text")
                
                # Create Twitter link if available
                twitter_element = html.P("🐦 Twitter: Not available", className="card-text")
                if pd.notna(row['twitter']) and is_valid_url(row['twitter']):
                    twitter_element = html.P([
                        "🐦 Twitter: ",
                        html.A(row['twitter'], href=row['twitter'], target="_blank", className="text-info")
                    ], className="card-text")
                
                # Create image element
                img_element = html.Div(className="text-center")
                if 'image_url' in row and pd.notna(row['image_url']) and is_valid_url(row['image_url']):
                    img_element = html.Div(
                        html.Img(
                            src=row['image_url'],
                            style={
                                'height': '150px',
                                'width': '150px',
                                'object-fit': 'cover',
                                'border-radius': '50%',
                                'border': '3px solid #ddd'
                            }
                        ),
                        className="text-center mb-3"
                    )
                elif 'image_url' in row and pd.notna(row['image_url']):
                    img_element = html.P("⚠️ Invalid image URL", className="text-center text-muted")
                else:
                    img_element = html.P("📷 No image available", className="text-center text-muted")
                
                card = dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                img_element,
                                html.H4(f"👤 {row['people']}", className="text-center mt-2 mb-3"),
                                html.P(f"💼 Designation: {row['designation']}", className="card-text text-center"),
                                linkedin_element,
                                twitter_element,
                                html.P(f"📝 Excerpt: {row['excerpt']}", className="card-text mt-3"),
                            ]
                        ),
                    ],
                    className="mb-4 shadow-sm p-3",
                    style={"border-radius": "10px"}
                )
                cards.append(card)
        
            # Create responsive grid layout for cards
            card_columns = []
            for i, card in enumerate(cards):
                card_columns.append(
                    dbc.Col(card, md=6, lg=4, className="mb-4")  # 3 columns on large screens, 2 on medium
                )
            
            people_details = html.Div([
                html.H3(f"👥 People at {company}", className="mt-4 mb-4 text-center border-bottom pb-2"),
                dbc.Row(card_columns, className="g-4")
            ])
        
        return company_details, people_details
    
    # For other levels (root or category), clear the details
    return html.Div(), html.Div()

if __name__ == '__main__':
    app.run(debug=True, port=8090)