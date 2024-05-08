function loadGoogleAnalytics(){
    var ga = document.createElement('script');
    ga.type = 'text/javascript';
    ga.async = true;
    ga.src = 'https://www.googletagmanager.com/gtag/js?id=UA-3843414-4';

    var s = document.getElementsByTagName('script')[0];
    s.parentNode.insertBefore(ga, s);
}

loadGoogleAnalytics(); //Create the script

window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());

gtag('config', 'UA-3843414-4');