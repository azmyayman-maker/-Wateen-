export interface NominatimResponse {
  place_id: number;
  lat: string;
  lon: string;
  display_name: string;
}

/**
 * Perform a fetch to Nominatim OSM API respecting User-Agent mandate.
 * Rate limiting logic (e.g. 1000ms debounce) is typically implemented by the caller.
 */
export async function searchAddress(query: string): Promise<NominatimResponse[]> {
  if (!query || query.trim() === '') return [];
  
  const url = new URL('https://nominatim.openstreetmap.org/search');
  url.searchParams.append('q', query);
  url.searchParams.append('format', 'jsonv2');
  url.searchParams.append('addressdetails', '1');
  url.searchParams.append('limit', '5');
  url.searchParams.append('accept-language', 'ar');

  try {
    const response = await fetch(url.toString(), {
      headers: {
        'User-Agent': 'WateenPlatform/1.0 (Integration/React)'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Nominatim HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data as NominatimResponse[];
  } catch (err) {
    console.error('Nominatim API Error:', err);
    return [];
  }
}
