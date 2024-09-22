import { DOMParser } from 'xmldom';

/**
 * Converts PNML content to a DOT string representation of a Petri net.
 * @param {string} pnmlContent - The PNML XML content as a string.
 * @returns {string} - The DOT string representation of the Petri net.
 */
export const convertPnmlToDot = (pnmlContent) => {
  try {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(pnmlContent, 'text/xml');
    const netElement = xmlDoc.getElementsByTagName('net')[0];
    
    let dotString = 'digraph PetriNet {\n';
    dotString += '  rankdir=LR;\n';
    dotString += '  node [shape=circle];\n';
    dotString += '  node [shape=box];\n\n';

    let uniqueResources = new Set();
    const colors = ['#D3D3D3', '#708090', '#696969', '#C0C0C0', '#F5F5F5', '#DCDCDC'];

    // Extract unique resources from places
    Array.from(netElement.getElementsByTagName('place')).forEach(place => {
      const placeName = place.getElementsByTagName('name')[0]?.getElementsByTagName('text')[0]?.textContent || place.getAttribute('id');
      if (placeName) {
        const resourceName = placeName.split(':')[0].trim();
        if (resourceName) {
          uniqueResources.add(resourceName);
        }
      }
    });

    uniqueResources = Array.from(uniqueResources);  
    
    // Add places to the DOT string
    Array.from(netElement.getElementsByTagName('place')).forEach(place => {
      const placeId = place.getAttribute('id');
      const placeName = place.getElementsByTagName('name')[0]?.getElementsByTagName('text')[0]?.textContent || placeId;
      if (placeId) {
        dotString += `  "${placeId}" [label="${placeName.split(':')[1]?.trim() || placeId}", shape=circle, color="${colors[uniqueResources.indexOf(placeName.split(':')[0].trim()) % uniqueResources.length]}"];\n`;
      }
    });

    // Add transitions to the DOT string
    Array.from(netElement.getElementsByTagName('transition')).forEach(transition => {
      const transitionId = transition.getAttribute('id');
      const transitionName = transition.getElementsByTagName('name')[0]?.getElementsByTagName('text')[0]?.textContent || transitionId;
      if (transitionId) {
        dotString += `  "${transitionId}" [label="${transitionName.split(':')[1]?.trim() || transitionId}", shape=box, color="${colors[uniqueResources.indexOf(transitionName.split(':')[0].trim()) % uniqueResources.length]}"];\n`;
      }
    });

    // Add arcs to the DOT string
    Array.from(netElement.getElementsByTagName('arc')).forEach(arc => {
      const arcSource = arc.getAttribute('source');
      const arcTarget = arc.getAttribute('target');
      dotString += `  "${arcSource}" -> "${arcTarget}";\n`;
    });

    dotString += '}\n';
    return dotString.replace(/:/g, "__"); // Replace colons in labels
  } catch (error) {
    console.error('Error parsing PNML to DOT:', error);
    return '';
  }
};