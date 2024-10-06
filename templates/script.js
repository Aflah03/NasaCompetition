const financialPlans = [
    {
      name: "Education Scholarship",
      description: "Provides funds for students pursuing higher education.",
      guidelines: "To be eligible for the Education Scholarship, applicants must demonstrate academic excellence and financial need. Applicants should provide proof of enrollment in an accredited institution, along with their latest transcripts. Additionally, a recommendation letter from a teacher or mentor may be required to showcase the applicant's commitment to their studies. The scholarship amount will depend on the applicant's financial situation and the availability of funds."
    },
    {
      name: "Medical Assistance",
      description: "Covers medical expenses for individuals in need.",
      guidelines: "Eligible applicants for the Medical Assistance program must provide medical documentation outlining their condition and the necessity for financial aid. Applicants must also submit proof of income to demonstrate financial need. The program aims to assist with essential medical treatments, medications, and related expenses. It is important to apply as early as possible, as funds are limited and awarded on a first-come, first-served basis."
    },
    {
      name: "Small Business Grant",
      description: "Offers grants to start or expand small businesses.",
      guidelines: "The Small Business Grant is designed for entrepreneurs looking to start or grow their businesses. To qualify, applicants must submit a detailed business plan outlining their business model, target market, and financial projections. Additionally, applicants should provide proof of any existing business licenses or registrations. The grant aims to foster innovation and economic growth, and successful applicants will be notified of funding decisions within 4-6 weeks."
    }
  ];
  
  document.getElementById('assistanceForm').addEventListener('submit', function(event) {
    event.preventDefault();
  
    const captchaInput = document.getElementById('captcha').value;
    const captchaAnswer = document.getElementById('captchaAnswer').value;
  
    if (captchaInput !== captchaAnswer) {
      alert("Incorrect CAPTCHA answer. Please try again.");
      return;
    }
  
    const fullName = document.getElementById('fullName').value;
  
    document.querySelector('.form-section').style.display = 'none';
    document.querySelector('.plans-section').style.display = 'block';
  
    document.getElementById('welcomeMessage').innerText = `Hello, ${fullName}. Based on your request, here are some financial plans that may suit your needs:`;
  
    const plansList = document.getElementById('plansList');
    plansList.innerHTML = '';
    financialPlans.forEach((plan, index) => {
      const planDiv = document.createElement('div');
      planDiv.classList.add('plan');
      planDiv.innerHTML = `
        <h3 onclick="showGuidelines(${index})">${plan.name}</h3>
        <p>${plan.description}</p>
      `;
      plansList.appendChild(planDiv);
    });
  });
  
  function goBack() {
    document.querySelector('.plans-section').style.display = 'none';
    document.querySelector('.form-section').style.display = 'block';
  }
  
  function goToNotifications() {
    document.querySelector('.form-section').style.display = 'none';
    document.querySelector('.plans-section').style.display = 'none';
    document.querySelector('.notifications-section').style.display = 'block';
  }
  
  function goBackToHome() {
    document.querySelector('.notifications-section').style.display = 'none';
    document.querySelector('.form-section').style.display = 'block';
  }
  
  function showGuidelines(index) {
    document.querySelector('.plans-section').style.display = 'none';
    document.querySelector('.guidelines-section').style.display = 'block';
  
    const guidelines = financialPlans[index].guidelines;
    document.getElementById('guidelineContent').innerText = guidelines;
  }
  
  function goBackToPlans() {
    document.querySelector('.guidelines-section').style.display = 'none';
    document.querySelector('.plans-section').style.display = 'block';
  }


  let index = 0;

function moveSlide(step) {
    const slider = document.querySelector('.slider');
    const slides = document.querySelectorAll('.slide');
    index += step;
    if (index >= slides.length) index = 0;
    if (index < 0) index = slides.length - 1;
    
    slider.style.transform = `translateX(-${index * 300}px)`; // Adjust based on the image size
}
