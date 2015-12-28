var setFocus = function() { document.s.q.focus(); };	
		var doSort = function() {
			var sortIndex = document.sortForm.sortField.selectedIndex;
			window.location = document.sortForm.sortField[sortIndex].value; };
		var showMore = function( facetCode ) {
			$("facet-list-ext-" + facetCode).style.display = "block";
			$('showmore-' + facetCode).style.display = "none";
			//$('cloudlink-' + facetCode).style.display = "none";
		};
            
        var showMoreAuthors = function( bib_num ) {
            $('show-more-authors-' + bib_num).style.display = "none";
            $('more-authors-' + bib_num).style.display="block";
        };
		
		var showAdvanced = function() {
			$('advanced-search').style.display="block";
			$('advanced-search').style.height="auto";
			$('advanced-search').style.padding="5px";
			
			$('show-advanced').style.display="none";
			$('basic-search').style.display="none";
			$('basic-search').style.height="0px";
			// now transfer anything in basic search form to the advanced search form
			alert("document.s.q is " + $('id_q').value     );
		};
		
        var doFacet = function( facetCode, searchString ) {
            //alert("search string is " + searchstring );
            //$('facet-list-replace-' + facetCode).innerHTML="howdy";
            //alert("facet code is " + facetCode + " search string is " + searchString);
            var facetURL = "/catalog/search/facet/?" + searchString + "&facet=" + facetCode;
            var callback = {
                success: function(o)  {
                    $('facet-list-replace-' + facetCode).innerHTML = o.responseText;
                },
                failure: function(o) {
                  //  alert('failure!');
                }
            
            };
            $('facet-list-replace-' + facetCode).innerHTML = "<br /><img src='http://catalog.spl.org/hipres/images/ajax-loader.gif' /><em class='blue'>Loading...</em>";
            var request = YAHOO.util.Connect.asyncRequest( 'GET', facetURL, callback );    
        };
		
		var checkNoImageAvailable = function() {
			// this function is used on the grid view to figure out if no cover image is available
			// for an item -- if not, display a "no image available" type image instead.  
			var jacketImages = $$('.cover');
			for( var i = 0; i < jacketImages.length; i++ ){
				var imgOn = jacketImages[i];
				if( imgOn.width == 1 && imgOn.height == 1 ) {
					imgOn.src = "{{PRESENTATION.NO_HITS_ICON}}";
				}
			}
		};