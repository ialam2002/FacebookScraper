# Facebook Scraper Application

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start Guide](#quick-start-guide)
- [Detailed User Guide](#detailed-user-guide)
- [Program Architecture](#program-architecture)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [Legal & Ethical Considerations](#legal--ethical-considerations)

## 🔍 Overview

The Facebook Scraper Application is a comprehensive Python-based GUI tool designed for scraping, analyzing, and visualizing Facebook friend networks and post interactions. Built with CustomTkinter for a modern interface and Selenium for web automation, it provides powerful capabilities for social network analysis and research.

### Key Capabilities:
- **Friend Network Scraping**: Extract friend lists from Facebook profiles
- **Post Likes Scraping**: Analyze who liked specific posts
- **Face Recognition Search**: Find profiles using facial recognition
- **Network Visualization**: Generate interactive graphs of connections
- **Data Export**: Export results to Excel, CSV, or JSON formats
- **Cross-Reference Analysis**: Find mutual connections between profiles

## ✨ Features

### 🔐 Authentication & Configuration
- Secure Facebook login with credential management
- Automated browser session handling
- ChromeDriver path detection and management
- Connection status monitoring

### 🕷️ Multi-Type Scraping
1. **Friend Network Scraping**
   - Extract complete friend lists from profiles
   - Configurable depth and limits
   - Handles both public and semi-private profiles
   - Progress tracking and status updates

2. **Post Likes Scraping**
   - Scrape people who liked specific posts
   - Support for multiple posts per profile
   - Handles infinite scroll and dynamic loading
   - Optional output file saving

3. **Profile Search & Face Matching**
   - Upload target photos for face recognition
   - Batch processing of multiple images
   - Similarity scoring and ranking
   - Profile picture extraction and comparison

### 📊 Data Analysis & Visualization
- **Interactive Network Graphs**: Powered by Plotly and NetworkX
- **Mutual Friends Analysis**: Find connections between profiles
- **Excel Export**: Comprehensive relationship matrices
- **Results Management**: Load, view, and organize scraped data

### 🎯 Smart Features
- **URL Normalization**: Handles various Facebook URL formats
- **Duplicate Detection**: Prevents redundant scraping
- **Memory-Only Mode**: Optional file-less operation
- **Background Processing**: Non-blocking operations with progress tracking

## 🚀 Installation

### Prerequisites
- **Python 3.8+** installed
- **Google Chrome browser** installed
- **Git** (optional, for cloning)

### Step 1: Download the Application
```bash
# Option 1: Clone the repository
git clone https://github.com/ialam2002/FacebookScraper.git
cd FacebookScraper

# Option 2: Download and extract the ZIP file
```

### Step 2: Install Dependencies
```bash
# Navigate to the application folder
cd facebook_scraper_app

# Install required packages
pip install -r requirements.txt
```

### Step 3: ChromeDriver Setup
The application includes ChromeDriver in the `chromedriver/` folder. If you need to update it:
1. Download ChromeDriver from https://chromedriver.chromium.org/
2. Replace `facebook_scraper_app/chromedriver/chromedriver.exe`
3. Ensure it matches your Chrome browser version

### Dependencies Overview
- **customtkinter**: Modern GUI framework
- **selenium**: Web automation and scraping
- **networkx**: Network graph analysis
- **plotly**: Interactive visualizations
- **pillow**: Image processing
- **opencv-python**: Computer vision operations
- **numpy**: Numerical computations
- **deepface**: Facial recognition
- **requests**: HTTP requests
- **pandas**: Data manipulation (optional for Excel export)
- **openpyxl**: Excel file handling

## 🎯 Quick Start Guide

### 1. Launch the Application
```bash
python main.py
```

### 2. Login to Facebook
1. Go to the **Config** tab
2. Enter your Facebook email and password
3. Click **Login** and wait for confirmation
4. Verify the status shows "Connected"

### 3. Start Scraping
**For Friend Networks:**
1. Switch to the **Scraping** tab
2. Enter Facebook profile URLs (one per line)
3. Configure settings (optional)
4. Click **Start Scraping**

**For Post Likes:**
1. Switch to the **Post Scraper** tab
2. Enter profile URLs whose posts you want to analyze
3. Set max posts limit (optional)
4. Click **Start Scraping**

### 4. View Results
1. Go to the **Results** tab to view scraped data
2. Use the **Visualization** tab for network graphs
3. Export data using the available export buttons

## 📖 Detailed User Guide

### Configuration Tab
**Purpose**: Manage Facebook login and browser settings

**Key Features:**
- **Login Form**: Enter Facebook credentials
- **Connection Status**: Real-time status monitoring
- **Browser Control**: Launch/close browser sessions
- **Settings**: Configure scraping parameters

**Best Practices:**
- Always login before starting any scraping operations
- Monitor connection status during long scraping sessions
- Use "Reopen Browser" if connection issues occur

### Scraping Tab (Friend Networks)
**Purpose**: Extract friend lists from Facebook profiles

**Input Options:**
- **Profile URLs**: Direct Facebook profile links
- **Batch Upload**: Excel/CSV/JSON files with multiple profiles
- **Depth Control**: How many degrees of separation to scrape
- **Limits**: Maximum friends per profile, total profiles

**Advanced Settings:**
- **Scroll Configuration**: Control page loading behavior
- **Delay Settings**: Prevent rate limiting
- **Output Format**: Choose file format for results

**Usage Tips:**
- Start with small batches to test settings
- Use depth 1 for direct friends only
- Monitor progress in the status area
- Save outputs to avoid data loss

### Post Scraper Tab
**Purpose**: Analyze who liked posts from specific profiles

**Key Features:**
- **Profile Input**: URLs of profiles whose posts to analyze
- **Post Limits**: Control how many posts per profile
- **Optional Output**: Can run without saving files
- **Progress Tracking**: Real-time updates

**How It Works:**
1. Navigates to each profile's posts
2. Finds posts with like buttons
3. Clicks to open likes popup
4. Extracts liker information
5. Scrolls through multiple posts

**Best Practices:**
- Enable post cap for faster processing
- Use specific profiles known to have engaging posts
- Monitor for popup handling issues

### Search Tab (Face Recognition)
**Purpose**: Find profiles using facial recognition technology

**Workflow:**
1. **Upload Target Image**: Photo of person to find
2. **Configure Search**: Set similarity thresholds
3. **Batch Processing**: Upload multiple target photos
4. **Review Results**: Browse matches with similarity scores
5. **Add to Scraper**: Send interesting profiles to other tabs

**Features:**
- **Similarity Scoring**: DeepFace-powered face matching
- **Profile Picture Extraction**: Automatic image retrieval
- **Batch Operations**: Process multiple searches
- **Integration**: Send results to scraping tabs

**Tips:**
- Use clear, front-facing photos for best results
- Adjust similarity thresholds based on results
- Review matches manually before adding to scraper

### Results Tab
**Purpose**: View, analyze, and export scraped data

**Data Views:**
- **Profile Summary**: Overview of scraped profiles
- **Friends Lists**: Detailed friend information
- **Network Statistics**: Connection counts and metrics
- **Search Results**: Face recognition matches

**Export Options:**
- **Excel Export**: Comprehensive relationship matrices
- **JSON Export**: Raw data for further processing
- **Network Export**: Graph data for external analysis

**Analysis Features:**
- **Mutual Friends**: Find shared connections
- **Profile Clustering**: Group related profiles
- **Statistics**: Network metrics and insights

### Visualization Tab
**Purpose**: Create and view interactive network graphs

**Graph Types:**
- **Friend Networks**: Node-link diagrams
- **Relationship Matrices**: Connection heatmaps
- **Cluster Analysis**: Community detection

**Interactive Features:**
- **Zoom & Pan**: Navigate large networks
- **Node Selection**: Click for profile details
- **Layout Options**: Different graph arrangements
- **Export**: Save graphs as images or HTML

## 🏗️ Program Architecture

### Core Components

#### 1. Main Application (`main.py`)
- **Entry Point**: Application startup and initialization
- **Dependency Checking**: Validates ChromeDriver and requirements
- **Splash Screen**: Loading screen during startup
- **Error Handling**: Global exception management

#### 2. GUI Framework (`gui/`)
- **`gui.py`**: Main application window and tab management
- **`config_tab.py`**: Login and configuration interface
- **`scraping_tab.py`**: Friend network scraping controls
- **`post_scraper_tab.py`**: Post likes scraping interface
- **`search_tab.py`**: Face recognition search tools
- **`results_tab.py`**: Data viewing and export functions
- **`visualization_tab.py`**: Graph creation and display
- **`scraper_control.py`**: Browser session management

#### 3. Scraping Engine (`scraper/`)
- **`scraper.py`**: Main friends scraping logic
- **`post_scraper.py`**: Post likes extraction
- **`search_profile_scraper.py`**: Profile search utilities
- **`search_group_profile_scraper.py`**: Group-based searching

#### 4. Face Recognition (`profile_search/`)
- **`search.py`**: Face matching and image processing
- **DeepFace Integration**: AI-powered face recognition
- **Image Processing**: Photo preparation and optimization

#### 5. Visualization Engine (`gui/visualization.py`)
- **NetworkX Integration**: Graph creation and analysis
- **Plotly Rendering**: Interactive visualization
- **Export Functions**: Graph saving and sharing

### Data Flow Architecture

```
[Facebook Login] → [Browser Session] → [Scraping Engine]
                                            ↓
[Raw Data] → [Processing & Normalization] → [Storage]
                                            ↓
[Results Tab] → [Visualization] → [Export Options]
     ↑              ↓
[Face Search] → [Profile Matching]
```

### Key Design Patterns

1. **Tab-Based Architecture**: Modular interface design
2. **Controller Pattern**: Centralized browser management
3. **Observer Pattern**: Progress updates and status monitoring
4. **Strategy Pattern**: Different scraping algorithms
5. **Factory Pattern**: Dynamic component creation

## 📚 Dependencies Deep Dive

### Core Dependencies
- **customtkinter (5.2.0+)**: Modern, theme-able GUI framework
- **selenium (4.0+)**: Web automation and browser control
- **Pillow (9.0+)**: Image processing and manipulation
- **requests (2.28+)**: HTTP client for web requests

### Data Processing
- **pandas (1.5+)**: Data manipulation and analysis
- **numpy (1.21+)**: Numerical computing foundation
- **openpyxl (3.0+)**: Excel file reading and writing

### Visualization
- **networkx (2.8+)**: Graph creation and analysis
- **plotly (5.15+)**: Interactive plotting and visualization

### AI/Computer Vision
- **opencv-python (4.6+)**: Computer vision library
- **deepface (0.0.75+)**: Facial recognition and analysis

### Optional Dependencies
- **matplotlib**: Alternative plotting backend
- **scikit-learn**: Additional ML algorithms
- **tensorflow**: DeepFace backend (auto-installed)

## 🛠️ Troubleshooting

### Common Issues

#### 1. ChromeDriver Problems
**Symptoms**: Browser won't open, WebDriver errors
**Solutions**:
- Update ChromeDriver to match your Chrome version
- Check file permissions on chromedriver.exe
- Verify Chrome installation path
- Try running as administrator

#### 2. Login Issues
**Symptoms**: Can't login to Facebook, authentication errors
**Solutions**:
- Use correct email/password combination
- Disable 2FA temporarily if possible
- Check for Facebook account restrictions
- Clear browser data and try again
- Use a different IP address if rate-limited

#### 3. Scraping Failures
**Symptoms**: No data collected, timeouts, errors
**Solutions**:
- Reduce scraping speed/add delays
- Check profile privacy settings
- Verify URLs are correct and accessible
- Monitor for Facebook layout changes
- Use smaller batch sizes

#### 4. Face Recognition Issues
**Symptoms**: No matches found, low accuracy
**Solutions**:
- Use high-quality, front-facing photos
- Ensure good lighting in reference images
- Adjust similarity thresholds
- Check DeepFace model installation
- Verify image formats are supported

#### 5. Memory/Performance Issues
**Symptoms**: Slow response, high RAM usage, crashes
**Solutions**:
- Reduce batch sizes
- Close other applications
- Increase virtual memory
- Use memory-only mode for temporary data
- Process data in smaller chunks

### Debug Mode
Enable detailed logging by modifying `main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files
- Check console output for error messages
- Browser logs available in developer tools
- Screenshot captures on failures (if enabled)

## ⚖️ Legal & Ethical Considerations

### Terms of Service Compliance
- **Facebook's Terms**: This tool may violate Facebook's Terms of Service
- **Rate Limiting**: Implement delays to avoid overwhelming servers
- **Respect Privacy**: Only scrape publicly available information
- **User Consent**: Ensure you have permission to analyze profiles

### Responsible Usage
- **Academic Research**: Primarily intended for research purposes
- **Data Protection**: Securely store and handle collected data
- **Anonymization**: Consider anonymizing data before sharing
- **Transparency**: Be open about data collection with stakeholders

### Legal Disclaimers
- **No Warranty**: Software provided as-is without guarantees
- **User Responsibility**: Users responsible for compliance with laws
- **Jurisdiction**: Consider local data protection regulations
- **Commercial Use**: Additional considerations for business applications

### Best Practices
1. **Minimize Data Collection**: Only collect what you need
2. **Secure Storage**: Encrypt sensitive data
3. **Regular Cleanup**: Delete old data periodically
4. **Access Controls**: Limit who can use the tool
5. **Documentation**: Keep records of data usage

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a virtual environment
3. Install development dependencies
4. Follow code style guidelines
5. Submit pull requests with tests

### Code Structure
- Follow Python PEP 8 style guide
- Use type hints where appropriate
- Document functions and classes
- Include unit tests for new features
- Update README for significant changes

## 📞 Support

### Getting Help
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check this README and code comments
- **Community**: Join discussions with other users

### Known Limitations
- Dependent on Facebook's current layout
- May require updates as Facebook changes
- Performance varies with network conditions
- Some profiles may be inaccessible due to privacy settings
- Face recognition accuracy depends on image quality

---

**Last Updated**: August 2025
**Version**: 2.0
**License**: MIT (see LICENSE file)

⚠️ **Disclaimer**: This tool is for educational and research purposes. Users are responsible for ensuring compliance with applicable laws and terms of service.
