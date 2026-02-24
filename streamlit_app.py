import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random

# Set the page layout to wide
st.set_page_config(layout="wide", page_title="AI Prioritization Dashboard")

# Initialize project list storage
if 'projects' not in st.session_state:
    st.session_state['projects'] = []

# ==========================================
# CONFIGURATION & HELPER FUNCTIONS
# ==========================================

AI_OPTIONS = [
    "No further tasks can be done with AI", 
    "Some tasks can be done with AI", 
    "Many tasks could be done with AI"
]

# The old quadrant names are now used as the "Operating Model" attribute
MODEL_OPTIONS = [
    "Onshore",
    "Offshore & Onshore",
    "Onshore + Automation",
    "Onshore + AI"
]

def get_marker_style(ai_potential, model):
    # 1. Color and Size based on AI Potential (Traffic Light System)
    if ai_potential == AI_OPTIONS[2]:    # Many tasks
        size = 34
        color = "#2ecc71" # Bright Green
    elif ai_potential == AI_OPTIONS[1]:  # Some tasks
        size = 24
        color = "#f1c40f" # Yellow/Gold
    else:                                # No tasks
        size = 14
        color = "#95a5a6" # Gray
        
    # 2. Shape based on the current operating model
    if model == MODEL_OPTIONS[0]: symbol = "circle"
    elif model == MODEL_OPTIONS[1]: symbol = "square"
    elif model == MODEL_OPTIONS[2]: symbol = "diamond"
    else: symbol = "triangle-up"
    
    return size, color, symbol

# ==========================================
# POP-UP DIALOG FUNCTIONS
# ==========================================

@st.dialog("Add New Project")
def add_submission_dialog():
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Project Name")
        
        st.markdown("**Strategic Scoring (1-10)**")
        impact = st.slider("Business Impact / ROI (1 = Low, 10 = High)", 1, 10, 5)
        ease = st.slider("Ease of Implementation (1 = Hard, 10 = Easy)", 1, 10, 5)
        
        st.markdown("**Project Details**")
        model = st.selectbox("Current Operating Model", MODEL_OPTIONS)
        ai_potential = st.selectbox("Potential for further AI tasks", AI_OPTIONS)
        
        col1, col2 = st.columns(2)
        if col1.form_submit_button("Submit", type="primary"):
            if name:
                # Jitter adjusted for the new 1-10 scale
                jx = random.uniform(-0.3, 0.3)
                jy = random.uniform(-0.3, 0.3)
                
                st.session_state['projects'].append({
                    "name": name,
                    "impact": impact,
                    "ease": ease,
                    "model": model,
                    "ai_potential": ai_potential,
                    "jx": jx,
                    "jy": jy,
                })
                st.rerun()
            else:
                st.error("Please enter a project name.")
        col2.form_submit_button("Clear")

@st.dialog("Edit Project")
def edit_submission_dialog(preselected_idx=0):
    if not st.session_state['projects']:
        st.info("No projects available to edit.")
        return
        
    project_names = [p['name'] for p in st.session_state['projects']]
    if preselected_idx >= len(project_names): preselected_idx = 0
        
    selected_name = st.selectbox("Select Project to Edit", project_names, index=preselected_idx)
    idx = project_names.index(selected_name)
    proj = st.session_state['projects'][idx]
    
    st.divider()
    
    new_name = st.text_input("Project Name", value=proj['name'])
    
    st.markdown("**Strategic Scoring (1-10)**")
    new_impact = st.slider("Business Impact / ROI", 1, 10, proj.get('impact', 5))
    new_ease = st.slider("Ease of Implementation", 1, 10, proj.get('ease', 5))
    
    st.markdown("**Project Details**")
    new_model = st.selectbox("Current Operating Model", MODEL_OPTIONS, index=MODEL_OPTIONS.index(proj.get('model', MODEL_OPTIONS[0])))
    new_ai = st.selectbox("Potential for further AI tasks", AI_OPTIONS, index=AI_OPTIONS.index(proj.get('ai_potential', AI_OPTIONS[0])))
    
    col1, col2 = st.columns(2)
    if col1.button("Save Changes", type="primary", use_container_width=True):
        proj.update({
            'name': new_name, 'impact': new_impact, 'ease': new_ease, 
            'model': new_model, 'ai_potential': new_ai
        })
        st.session_state['projects'][idx] = proj
        st.rerun()
        
    if col2.button("Delete Project", use_container_width=True):
        st.session_state['projects'].pop(idx)
        st.rerun()

# ==========================================
# MAIN PAGE LAYOUT
# ==========================================

col_title, col_empty, col_add, col_edit = st.columns([5, 1, 1.5, 1.5])

with col_title:
    st.title("AI Prioritization Dashboard")
    st.markdown("Target the largest, greenest dots in the **Quick Wins** quadrant.")

with col_add:
    st.write("") 
    if st.button("➕ Add Submission", use_container_width=True): add_submission_dialog()

with col_edit:
    st.write("") 
    if st.button("✏️ Edit Submission", use_container_width=True): edit_submission_dialog()

# Visual Legend
st.info("**Color = AI Potential:** 🟢 Many Tasks | 🟡 Some Tasks | ⚪ No Tasks &nbsp;&nbsp;&nbsp; **Shape = Model:** ● Onshore | ■ Offshore & Onshore | ◆ Onshore + Automation | ▲ Onshore + AI")

projects = st.session_state['projects']

# ==========================================
# PLOTLY GRID GENERATION
# ==========================================

fig = go.Figure()

# Set up the Value vs Effort Matrix layout
fig.update_layout(
    shapes=[
        # Crosshairs at the middle (5.5 on a 1-10 scale)
        dict(type='line', x0=5.5, x1=5.5, y0=0.5, y1=10.5, line=dict(color='gray', dash='dash')),
        dict(type='line', x0=0.5, x1=10.5, y0=5.5, y1=5.5, line=dict(color='gray', dash='dash'))
    ],
    xaxis=dict(range=[0.5, 10.5], title='<b>Ease of Implementation</b> (1 = Hard, 10 = Easy) →', dtick=1),
    yaxis=dict(range=[0.5, 10.5], title='<b>Business Impact / ROI</b> (1 = Low, 10 = High) →', dtick=1),
    height=750, # Slightly shorter to make room for the table below
    margin=dict(t=40, b=40, l=40, r=40) 
)

# Background Quadrant Labels
fig.update_layout(
    annotations=[
        dict(x=8, y=8, text="<b>QUICK WINS</b><br>(High Impact, Easy)", font=dict(size=24, color="rgba(150,150,150,0.2)"), showarrow=False, align="center"),
        dict(x=3, y=8, text="<b>MAJOR PROJECTS</b><br>(High Impact, Hard)", font=dict(size=24, color="rgba(150,150,150,0.2)"), showarrow=False, align="center"),
        dict(x=8, y=3, text="<b>FILL-INS</b><br>(Low Impact, Easy)", font=dict(size=24, color="rgba(150,150,150,0.2)"), showarrow=False, align="center"),
        dict(x=3, y=3, text="<b>RE-EVALUATE</b><br>(Low Impact, Hard)", font=dict(size=24, color="rgba(150,150,150,0.2)"), showarrow=False, align="center"),
    ]
)

if projects:
    xs = [p['ease'] + p.get('jx', 0) for p in projects]
    ys = [p['impact'] + p.get('jy', 0) for p in projects]
    names = [p['name'] for p in projects]
    
    # Generate styles for each dot
    sizes, colors, symbols = [], [], []
    for p in projects:
        sz, col, sym = get_marker_style(p.get('ai_potential'), p.get('model'))
        sizes.append(sz)
        colors.append(col)
        symbols.append(sym)
    
    fig.add_trace(go.Scatter(
        x=xs, y=ys, 
        mode='markers+text',         
        text=names,                  
        textposition='top center',   
        marker=dict(size=sizes, color=colors, symbol=symbols, line=dict(width=1, color='DarkSlateGrey')),        
        customdata=list(range(len(projects))),
        hoverinfo='text',
        hovertext=[f"<b>{p['name']}</b><br>Impact: {p['impact']} | Ease: {p['ease']}<br>Model: {p['model']}<br>AI Potential: {p['ai_potential']}" for p in projects] 
    ))

# Render the interactive plot
event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")

# Click-to-edit functionality
if "selection" in event and "points" in event["selection"] and len(event["selection"]["points"]) > 0:
    clicked_idx = event["selection"]["points"][0]["customdata"]
    edit_submission_dialog(preselected_idx=clicked_idx)

# ==========================================
# DATA HUB (SORTABLE TABLE)
# ==========================================

st.divider()
st.subheader("Project Data Hub")

if projects:
    # Convert session state to a pandas dataframe
    df = pd.DataFrame(projects)
    
    # Filter out the jitter coordinates and rearrange columns for the user
    display_df = df[['name', 'impact', 'ease', 'model', 'ai_potential']].copy()
    display_df.columns = ["Project Name", "Business Impact (1-10)", "Ease of Implementation (1-10)", "Current Model", "AI Potential"]
    
    # Automatically sort to bubble the best projects (High Impact, High Ease) to the top
    display_df = display_df.sort_values(by=["Business Impact (1-10)", "Ease of Implementation (1-10)"], ascending=[False, False])
    
    # Display the interactive table
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("Add a project to see the data table.")
