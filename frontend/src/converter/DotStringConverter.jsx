export const convertPnmlToDot = (pnmlContent) => {
  try {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(pnmlContent, 'text/xml');
    const netElement = xmlDoc.getElementsByTagName('net')[0];
    
    let dotString = 'digraph PetriNet {\n';
    dotString += '  rankdir=LR;\n';
    dotString += '  node [shape=circle];\n'; // Default shape for places
    dotString += '  node [shape=box];\n'; // Default shape for transitions

    // Colors for different markings
    const initialMarkingColor = '#007070'; // Teal for initial marking
    const finalMarkingColor = '#007070'; // Teal for final marking
    const normalColor = '#ffffff'; // Default color for places

    // Add places to the DOT string
    Array.from(netElement.getElementsByTagName('place')).forEach(place => {
      const placeId = place.getAttribute('id');
      const placeName = place.getElementsByTagName('name')[0]?.getElementsByTagName('text')[0]?.textContent || placeId;
      const initialMarking = place.getElementsByTagName('initialMarking')[0]?.getElementsByTagName('text')[0]?.textContent;
      
      // Use a set for final markings
      const finalMarkings = new Set(
        Array.from(netElement.getElementsByTagName('finalmarkings')[0]?.getElementsByTagName('marking')).map(marking => 
          marking.getElementsByTagName('place')[0].getAttribute('idref')
        )
      );

      let color = normalColor; // Default color
      let penWidth = 1; // Default border thickness

      if (initialMarking) {
        color = initialMarkingColor;
        penWidth = 3; // Increase border thickness for initial marking
      } else if (finalMarkings.has(placeId)) {
        color = finalMarkingColor;
        penWidth = 3; // Increase border thickness for final marking
      }

      if (placeId) {
        dotString += `  "${placeId}" [label="${placeName}", shape=circle, style="filled", fillcolor="${color}", penwidth="${penWidth}"];\n`;
      }
    });


    // Add transitions to the DOT string
    Array.from(netElement.getElementsByTagName('transition')).forEach(transition => {
      const transitionId = transition.getAttribute('id');
      const transitionName = transition.getElementsByTagName('name')[0]?.getElementsByTagName('text')[0]?.textContent || transitionId;

      if (transitionId) {
        const fillColor = (transitionId.includes('tau') || transitionId.includes('skip')) ? 'black' : 'white';

        dotString += `  "${transitionId}" [label="${transitionName || transitionId}", shape=box, style="filled", fillcolor="${fillColor}"];\n`;
      }
    });


    // Add arcs to the DOT string
    Array.from(netElement.getElementsByTagName('arc')).forEach(arc => {
      const arcSource = arc.getAttribute('source');
      const arcTarget = arc.getAttribute('target');
      dotString += `  "${arcSource}" -> "${arcTarget}";\n`;
    });

    dotString += '}\n';
    return dotString.replace(/:/g, "__"); // Replace colons in labels to avoid DOT syntax issues
  } catch (error) {
    console.error('Error parsing PNML to DOT:', error);
    return '';
  }
};
