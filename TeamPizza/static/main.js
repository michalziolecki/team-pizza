const navSlide = () => {
	const stack = document.querySelector('.stack');
	const nav = document.querySelector('.nav-links');
	const navLinks = document.querySelectorAll('.nav-links li');

	stack.addEventListener('click', ()=>{
		nav.classList.toggle('nav-active');
		//Animate links
		navLinks.forEach((link, index)=>{
			if (link.style.animation) {
				link.style.animation = '';
			} else {
				link.style.animation = `navLinkFade 0.5s ease forwards ${index / 7 + 0.3}s`;
				console.log(index/7);
			}
		})

		//stack animation
		stack.classList.toggle('toggle');
	});
}

navSlide();