class CustomIframeCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  setConfig(config) {
/*
    if (!config.entity) {
      throw new Error('Please define an entity');
    }
*/

    const root = this.shadowRoot;
    if (root.lastChild) root.removeChild(root.lastChild);
    const cardConfig = Object.assign({}, config);
    if (!cardConfig.scale) cardConfig.scale = "50px";
    if (!cardConfig.from) cardConfig.from = "left";
    const card = document.createElement('ha-card');
    
    const content = document.createElement('div');
    content.id = "theiframe";
    card.appendChild(content);

    const resp = document.createElement('div');
    resp.classList.add("resp-container");
    content.appendChild(resp);
    


    	const ifrm = document.createElement("iframe");
        ifrm.setAttribute("src", config.url);
        ifrm.classList.add("resp-iframe");
        ifrm.setAttribute("sandbox", "allow-same-origin allow-scripts allow-popups allow-forms");
		resp.appendChild(ifrm);
		
    const style = document.createElement('style');
    style.textContent = `
      ha-card {
	  	height: 100%;
	  	background:none;
	  	box-shadow:none;
	  	    border-radius: 0.8vw;
	  	    overflow:hidden;
      }
      #value {
        font-size: calc(var(--base-unit) * 1.3);
        line-height: calc(var(--base-unit) * 1.3);
        color: var(--primary-text-color);
      }
     .resp-container {
	    position: relative;
	    overflow: hidden;
	    padding-top: 80%;
	 }
	 #theiframe{
	 
	 	height: 100%;
	 }
	 .resp-iframe {
	    position: absolute;
	    top: 0;
	    left: 0;
	    width: 100%;
	    height: 100%;
	    border: 0;
	 }
    `;

    card.appendChild(style);
    root.appendChild(card);
    
    
   

    
    this._config = cardConfig;
  }


  set hass(hass) {
    const config = this._config;
    const root = this.shadowRoot;



    root.lastChild.hass = hass;
  }

  getCardSize() {
    return 1;
  }
}

customElements.define('custom-iframe', CustomIframeCard);
