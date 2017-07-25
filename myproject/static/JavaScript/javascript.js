var up_button = document.getElementById("upvote_button");



up_button.addEventListener('click',function(){
	if((up_button).value=="Upvote"){
		up_button.value="Downvote";
	}

    else{
    	up_button.value="Upvote";
    }

});