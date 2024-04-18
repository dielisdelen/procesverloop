document.addEventListener('DOMContentLoaded', function() {
  console.log(document.getElementById('timelineContainer'));
  const timelineContainer = document.getElementById('timelineContainer');
  console.log(timelineContainer); // Verify this is not null
  const ecliId = timelineContainer.getAttribute('data-ecli-id');

  if (ecliId) {
      fetch(`/api/get-data?ecli_id=${ecliId}`)
          .then(response => {
              if (!response.ok) {
                  throw new Error('Network response was not ok');
              }
              return response.json();
          })
          .then(data => {
            // For debugging
            console.log(data);
            const openaiData = JSON.parse(data.openai_response);

            // Display general information
            document.getElementById('ecli').textContent = `ECLI: ${openaiData.generalInfo.ECLI}`;
            document.getElementById('court').textContent = `${data.instantie}`;
            document.getElementById('standpunt_eiser').textContent = `${openaiData.legalDetails.claimsOfPlaintiff || openaiData.legalDetails.claimsVanEiser}`;
            document.getElementById('standpunt_verweerder').textContent = `${openaiData.legalDetails.defenceOfDefendant || openaiData.legalDetails.verdedigingVanGedaagde}`;
            document.getElementById('oordeel_rechter').textContent = `${openaiData.legalDetails.conclusionOfCourt || openaiData.legalDetails.conclusieVanRechter}`;
            document.getElementById('vonnis_in_emojis').textContent = `${openaiData.legalDetails.emojiSummary}`;

            // Find the placeholder where the URL should be inserted
            const urlPlaceholder = document.getElementById('urlPlaceholder');

            // Create the anchor element for the URL
            const urlLinkElement = document.createElement('a');
            urlLinkElement.href = openaiData.generalInfo.url;
            urlLinkElement.textContent = 'rechtspraak.nl'; // or any other text you want for the link
            urlLinkElement.target = "_blank"; // Ensures the link opens in a new tab
        
            // Replace the placeholder with the URL link
            urlPlaceholder.replaceWith(urlLinkElement);

            // Process and display timeline entries
            const eventList = document.getElementById('eventList');
            openaiData.timelineEntries.forEach(event => {
              // Create the main container for the event item
              const eventItem = document.createElement('li');
              eventItem.className = 'event-item';

              // Create and fill the left content with date
              const leftContent = document.createElement('div');
              leftContent.className = 'left-content';
              const dateParagraph = document.createElement('p');
              dateParagraph.className = 'date_label';
              dateParagraph.textContent = event.date;
              leftContent.appendChild(dateParagraph);

              // Create and fill the right content with the party and description
              const rightContent = document.createElement('div');
              rightContent.className = 'right-content';
              const partyParagraph = document.createElement('p');
              partyParagraph.className = 'party_label';
              partyParagraph.textContent = event.party;
              const descriptionParagraph = document.createElement('p');
              descriptionParagraph.className = 'description_text';
              descriptionParagraph.textContent = event.event;
              rightContent.appendChild(partyParagraph);
              rightContent.appendChild(descriptionParagraph);

              // Assemble the event item
              eventItem.appendChild(leftContent);
              eventItem.appendChild(rightContent);

              // Append the event item to the timeline
              eventList.appendChild(eventItem);
            });
          })
          .catch(error => {
              console.error('Error fetching the timeline data:', error);
          });
  } else {
      console.error('ECLI ID not found');
  }
});
