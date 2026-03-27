# Power BI Dashboard Guide — Global AI Index (2015-2026)

## Part B: Business Intelligence Approach

This guide walks you through building a 3-page interactive dashboard in Power BI Desktop using the cleaned dataset.

---

## Step 1: Import Data

1. Open **Power BI Desktop**
2. Click **Home > Get Data > Text/CSV**
3. Browse to `ai_index_cleaned.csv` and click **Open**
4. In the preview, verify columns look correct, then click **Load**
5. In the right panel, you should see the table with all 29 columns

---

## Step 2: Verify Data Types

1. Go to **Model view** (left sidebar, table icon)
2. Click on the `ai_index_cleaned` table
3. Verify these types (change if needed by clicking column header > Data type):
   - `year` → **Whole Number**
   - `country`, `region`, `iso_code` → **Text**
   - All other columns → **Decimal Number**

---

## Step 3: Create Measures (DAX)

Click **Home > New Measure** and add each of these:

```dax
Avg AI Score = AVERAGE(ai_index_cleaned[ai_index_score])
```

```dax
Total Investment = SUM(ai_index_cleaned[ai_investment_billion_usd])
```

```dax
Avg Readiness = AVERAGE(ai_index_cleaned[ai_readiness_score])
```

```dax
Country Count = DISTINCTCOUNT(ai_index_cleaned[country])
```

---

## Page 1: Global Overview

### Layout:
```
┌──────────────────────────────────────────────────┐
│  [Year Slicer]    [Region Slicer]                │
├──────────┬──────────┬──────────┬─────────────────┤
│ Card:    │ Card:    │ Card:    │ Card:            │
│ Avg AI   │ Total    │ Country  │ Avg Readiness    │
│ Score    │ Invest.  │ Count    │                  │
├──────────┴──────────┴──────────┴─────────────────┤
│                                                   │
│          Choropleth Map (Full Width)              │
│                                                   │
├──────────────────────┬───────────────────────────┤
│  Bar Chart:          │  Line Chart:              │
│  Top 10 by AI Score  │  AI Score Trend Over Time │
└──────────────────────┴───────────────────────────┘
```

### Step-by-step:

#### A. Year Slicer
1. From **Visualizations** panel, select **Slicer**
2. Drag `year` to the slicer
3. Click the slicer > Format > Slicer settings > Style > **Dropdown** (or **Between** for range)
4. Set default to show all years

#### B. Region Slicer
1. Add another **Slicer**
2. Drag `region` into it
3. Format > Slicer settings > Selection > Turn on **Multi-select with Ctrl**

#### C. KPI Cards (4 cards)
1. Add a **Card** visual
2. Drag `Avg AI Score` measure to it
3. Format: Font size 28, Bold, add title "Avg AI Score"
4. Repeat for `Total Investment`, `Country Count`, `Avg Readiness`
5. Arrange them in a row at the top

#### D. Choropleth Map
1. Add a **Map** visual (or **Shape Map** for filled regions)
2. Drag `country` to **Location**
3. Drag `ai_index_score` to **Color saturation**
4. Format > Map settings > Theme > **Viridis** or similar gradient
5. Add `ai_global_rank` to **Tooltips**
6. Resize to fill the middle section

#### E. Bar Chart — Top 10 Countries
1. Add a **Clustered Bar Chart**
2. Drag `country` to **Y-axis**
3. Drag `ai_index_score` to **X-axis**
4. In the Filters pane, set **Top N** filter on `country`:
   - Show items: **Top 10**
   - By value: `ai_index_score`
5. Format: Data colors > use a gradient or single color

#### F. Line Chart — Trend Over Time
1. Add a **Line Chart**
2. Drag `year` to **X-axis**
3. Drag `ai_index_score` to **Y-axis** (Average)
4. Drag `country` to **Legend**
5. Format: Line width 2, markers on

---

## Page 2: Country Deep Dive

### Layout:
```
┌──────────────────────────────────────────────────┐
│  [Country Dropdown]    [Year Range Slicer]        │
├──────────┬──────────┬──────────┬─────────────────┤
│ Card:    │ Card:    │ Card:    │ Card:            │
│ AI Score │ Rank     │ Invest.  │ Startups         │
├──────────┴──────────┴──────────┴─────────────────┤
│                                                   │
│     Gauge Charts (Row of 5 - Key Dimensions)     │
│  Adoption | Infra | Research | Gov | Commercial   │
│                                                   │
├──────────────────────┬───────────────────────────┤
│  Area Chart:         │  Table:                   │
│  Score Trend         │  All Metrics for Selected │
│  Over Years          │  Country                  │
└──────────────────────┴───────────────────────────┘
```

### Step-by-step:

#### A. Country Dropdown Slicer
1. Add **Slicer** > drag `country`
2. Format: Style > **Dropdown**
3. Default selection: USA

#### B. Year Range Slicer
1. Add **Slicer** > drag `year`
2. Style: **Between** (creates a range slider)

#### C. KPI Cards
1. Add 4 **Card** visuals:
   - `ai_index_score` (Average)
   - `ai_global_rank` (Minimum — to show best rank)
   - `ai_investment_billion_usd` (Sum)
   - `ai_startups_count` (Average)

#### D. Gauge Charts (5 gauges in a row)
For each dimension:
1. Add a **Gauge** visual
2. Set **Value** to the average of the column
3. Set **Min** to 0, **Max** to 100
4. Title each one clearly

| Gauge | Column |
|-------|--------|
| Adoption | `ai_adoption_consumer` |
| Infrastructure | `cloud_infrastructure` |
| Research | `ai_policy_score` |
| Government | `ai_regulation_score` |
| Commercial | `ai_startups_count` (normalized) |

#### E. Area Chart
1. Add **Area Chart**
2. `year` on X-axis
3. `ai_index_score` on Y-axis
4. This will filter automatically based on the country slicer

#### F. Detail Table
1. Add a **Table** visual
2. Drag columns: `year`, `ai_index_score`, `ai_global_rank`, `ai_investment_billion_usd`, `ai_research_papers`, `ai_readiness_score`
3. Format: Alternating rows, header bold

---

## Page 3: Country Comparison

### Layout:
```
┌──────────────────────────────────────────────────┐
│  [Multi-Select Country Slicer]  [Year Slicer]    │
├─────────────────────────────────────────────────-┤
│                                                   │
│   Clustered Bar Chart: Side-by-Side Comparison   │
│   (Countries on X, AI Score on Y, Color=Country) │
│                                                   │
├──────────────────────┬───────────────────────────┤
│  Scatter Plot:       │  Multi-Line Chart:        │
│  GDP vs AI Score     │  Selected Countries       │
│  (bubble = invest)   │  Score Over Time          │
├──────────────────────┴───────────────────────────┤
│                                                   │
│   Matrix / Table: Full Comparison Grid           │
│   Countries as rows, key metrics as columns      │
└──────────────────────────────────────────────────┘
```

### Step-by-step:

#### A. Multi-Select Country Slicer
1. Add **Slicer** > drag `country`
2. Style: **List** (with checkboxes)
3. Enable multi-select
4. Pre-select: USA, China, Germany, UK, Japan

#### B. Clustered Bar Chart
1. Add **Clustered Bar Chart**
2. `country` on Y-axis
3. `ai_index_score` on X-axis
4. `country` on Legend (for color coding)

#### C. Scatter Plot
1. Add **Scatter Chart**
2. `gdp_per_capita` on X-axis
3. `ai_index_score` on Y-axis
4. `ai_investment_billion_usd` on Size
5. `country` on Legend
6. Add `year` to **Play Axis** for animation (optional)
7. Add `region` and `ai_global_rank` to **Tooltips**

#### D. Multi-Line Chart
1. Add **Line Chart**
2. `year` on X-axis
3. `ai_index_score` on Y-axis
4. `country` on Legend
5. Filters auto-applied from slicer

#### E. Comparison Matrix
1. Add **Matrix** visual
2. `country` on Rows
3. Add to Values: `ai_index_score`, `ai_readiness_score`, `ai_investment_billion_usd`, `ai_startups_count`, `ai_research_papers`
4. Format: Conditional formatting (color scale) on each value column
   - Right-click column > Conditional formatting > Background color > Color scale

---

## Step 4: Design & Formatting

### Color Theme (Colorblind-Safe)
1. Go to **View > Themes > Browse for themes**
2. Or manually set these colors across all visuals:
   - Primary: `#0077BB` (blue)
   - Secondary: `#EE6677` (red)
   - Accent 1: `#009988` (teal)
   - Accent 2: `#EE7733` (orange)
   - Accent 3: `#33BBEE` (cyan)

### General Formatting
- **Title**: Each page should have a text box title at the top
  - Page 1: "Global AI Index — Overview (2015-2026)"
  - Page 2: "Country Deep Dive"
  - Page 3: "Country Comparison"
- **Background**: White or very light gray (#F8F8F8)
- **Font**: Segoe UI, consistent sizes (Title: 18pt, Card values: 28pt, Labels: 10pt)
- **Borders**: Light gray borders on cards for clean separation

### Tooltips
- On each chart, add extra fields to **Tooltips** well:
  - `region`, `ai_global_rank`, `ai_readiness_score`
- This allows viewers to hover and explore without cluttering the visual

### Interactions
1. Go to **Format > Edit Interactions**
2. Ensure slicers filter all visuals on the same page
3. For the bar chart on Page 1: set it to **highlight** (not filter) the line chart

---

## Step 5: Publish / Export

1. **Save** as `.pbix` file in the project folder
2. To share: **File > Export to PDF** or **Publish to Power BI Service** (if you have a school account)
3. For submission: include both the `.pbix` file and a PDF export

---

## Estimated Time: 20-30 minutes following these steps.
