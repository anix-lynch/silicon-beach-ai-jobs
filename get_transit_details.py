#!/usr/bin/env python3
"""
Helper script to get detailed transit directions with actual bus lines
Uses Google Directions API (more detailed than Distance Matrix)
"""

import json
import requests
import sys

def get_detailed_transit(origin, destination, api_key):
    """
    Get detailed transit directions including:
    - Bus line numbers (Culver CityBus, Big Blue Bus, Metro)
    - Number of transfers
    - Walking portions
    - Exact route
    """
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    
    params = {
        'origin': origin,
        'destination': destination,
        'mode': 'transit',
        'transit_mode': 'bus|rail',
        'departure_time': 'now',
        'key': api_key
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=15)
        data = response.json()
        
        if data['status'] == 'OK':
            route = data['routes'][0]
            leg = route['legs'][0]
            
            result = {
                'total_duration': leg['duration']['text'],
                'total_distance': leg['distance']['text'],
                'steps': [],
                'transit_lines': [],
                'total_transfers': 0
            }
            
            for step in leg['steps']:
                step_info = {
                    'mode': step['travel_mode'],
                    'duration': step['duration']['text'],
                    'instructions': step.get('html_instructions', '').replace('<b>', '').replace('</b>', '')
                }
                
                # If this is a transit step, get the line details
                if step['travel_mode'] == 'TRANSIT':
                    transit = step.get('transit_details', {})
                    line = transit.get('line', {})
                    
                    vehicle_type = line.get('vehicle', {}).get('type', 'Bus')
                    line_name = line.get('short_name', line.get('name', 'Unknown'))
                    agency = line.get('agencies', [{}])[0].get('name', 'Unknown')
                    
                    departure_stop = transit.get('departure_stop', {}).get('name', '')
                    arrival_stop = transit.get('arrival_stop', {}).get('name', '')
                    num_stops = transit.get('num_stops', 0)
                    
                    step_info.update({
                        'vehicle': vehicle_type,
                        'line': line_name,
                        'agency': agency,
                        'from_stop': departure_stop,
                        'to_stop': arrival_stop,
                        'num_stops': num_stops
                    })
                    
                    result['transit_lines'].append(f"{agency} {line_name}")
                    result['total_transfers'] += 1
                
                result['steps'].append(step_info)
            
            # Subtract 1 because first transit line isn't a transfer
            if result['total_transfers'] > 0:
                result['total_transfers'] -= 1
            
            return result
        else:
            return {'error': data.get('status', 'Unknown error')}
            
    except Exception as e:
        return {'error': str(e)}

def format_transit_route(transit_info):
    """Format transit info nicely"""
    if 'error' in transit_info:
        return f"Error: {transit_info['error']}"
    
    output = []
    output.append(f"\n📍 Total: {transit_info['total_duration']} ({transit_info['total_distance']})")
    output.append(f"🔄 Transfers: {transit_info['total_transfers']}")
    
    if transit_info['transit_lines']:
        output.append(f"🚌 Lines: {' → '.join(transit_info['transit_lines'])}")
    
    output.append("\n📋 Route Details:")
    
    for i, step in enumerate(transit_info['steps'], 1):
        if step['mode'] == 'TRANSIT':
            output.append(f"\n  {i}. {step['vehicle']}: {step['agency']} {step['line']}")
            output.append(f"     Board at: {step['from_stop']}")
            output.append(f"     Get off at: {step['to_stop']}")
            output.append(f"     Duration: {step['duration']} ({step['num_stops']} stops)")
        elif step['mode'] == 'WALKING':
            output.append(f"\n  {i}. 🚶 Walk: {step['duration']}")
            output.append(f"     {step['instructions']}")
    
    return '\n'.join(output)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python get_transit_details.py <destination> <api_key>")
        print("Example: python get_transit_details.py 'Beverly Hills, CA' YOUR_API_KEY")
        sys.exit(1)
    
    origin = "YOUR_HOME_ADDRESS"
    destination = sys.argv[1]
    api_key = sys.argv[2]
    
    print(f"🔍 Getting transit directions from Culver City to {destination}...\n")
    
    transit_info = get_detailed_transit(origin, destination, api_key)
    print(format_transit_route(transit_info))

