// DOM Elements
const locationInput = document.getElementById('locationInput');
const searchBtn = document.getElementById('searchBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const results = document.getElementById('results');

// Search for location
async function searchLocation(query) {
    const searchTerm = query || locationInput.value.trim();
    
    if (!searchTerm) {
        showError('PLEASE ENTER A VILLAGE OR MANDAL NAME');
        return;
    }
    
    // Show loading
    loading.classList.remove('hidden');
    error.classList.add('hidden');
    results.classList.add('hidden');
    
    try {
        const response = await fetch(`/search?q=${encodeURIComponent(searchTerm)}`);
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        displayResults(data);
    } catch (err) {
        showError('FAILED TO FETCH WEATHER DATA. PLEASE TRY AGAIN.');
    } finally {
        loading.classList.add('hidden');
    }
}

// Display weather results
function displayResults(data) {
    const { location, weather } = data;
    
    // Location Info
    document.getElementById('villageName').textContent = location.village.toUpperCase();
    
    let hierarchy = '';
    if (location.mandal) hierarchy += `MANDAL: ${location.mandal.toUpperCase()} | `;
    if (location.district) hierarchy += `DISTRICT: ${location.district.toUpperCase()} | `;
    if (location.state) hierarchy += `STATE: ${location.state.toUpperCase()}`;
    document.getElementById('locationHierarchy').textContent = hierarchy;
    
    document.getElementById('coordinates').textContent = 
        `COORDINATES: ${location.latitude.toFixed(4)}°N, ${location.longitude.toFixed(4)}°E`;
    
    // Weather Card
    document.getElementById('temperature').textContent = weather.temperature;
    document.getElementById('conditionIcon').textContent = weather.icon;
    document.getElementById('condition').textContent = weather.condition.toUpperCase();
    document.getElementById('feelsLike').textContent = `FEELS LIKE ${weather.feels_like}°C`;
    document.getElementById('localTime').textContent = `LOCAL TIME: ${weather.local_time}`;
    
    // Details
    document.getElementById('humidity').textContent = `${weather.humidity}%`;
    document.getElementById('windSpeed').textContent = `${weather.wind_speed} KM/H ${weather.wind_direction}`;
    document.getElementById('pressure').textContent = `${weather.pressure} HPA`;
    document.getElementById('cloudCover').textContent = `${weather.cloud_cover}%`;
    
    // Forecast
    const forecastGrid = document.getElementById('forecast');
    forecastGrid.innerHTML = weather.forecast.map(day => `
        <div class="forecast-card">
            <div class="forecast-day">${day.day}</div>
            <div class="forecast-date">${day.date}</div>
            <div class="forecast-icon">${day.icon}</div>
            <div class="forecast-temps">
                <span class="forecast-high">${day.high}°</span>
                <span class="forecast-low">/ ${day.low}°</span>
            </div>
            <div class="forecast-rain">🌧️ ${day.rain_chance}% RAIN</div>
        </div>
    `).join('');
    
    // Last Updated
    document.getElementById('lastUpdated').textContent = weather.last_updated;
    
    // Show results
    results.classList.remove('hidden');
}

// Show error message
function showError(message) {
    error.textContent = message;
    error.classList.remove('hidden');
    loading.classList.add('hidden');
    results.classList.add('hidden');
}

// Event Listeners
searchBtn.addEventListener('click', () => searchLocation());

locationInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchLocation();
    }
});

// Initial focus
locationInput.focus();