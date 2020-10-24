((LitElement) => {
    console.info(
        '%c MULTIPLE-ENTITY-ROW %c 3.5.1 ',
        'color: cyan; background: black; font-weight: bold;',
        'color: darkblue; background: white; font-weight: bold;',
    );

    const html = LitElement.prototype.html;
    const css = LitElement.prototype.css;

    const UNAVAILABLE = 'unavailable';
    const UNKNOWN = 'unknown';

    class MultipleEntityRow extends LitElement {

        static get properties() {
            return {
                _hass: {},
                _config: {},
                state: {},
            }
        }

        static get styles() {
            return css`
          :host {
            display: flex;
            align-items: center;
          }
          .flex {
            flex: 1;
            margin-left: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            min-width: 0;
          }
          .info {
            flex: 1 0 60px;
            cursor: pointer;
          }
          .info, .info > * {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .flex ::slotted(*) {
            margin-left: 8px;
            min-width: 0;
          }
          .flex ::slotted([slot="secondary"]) {
            margin-left: 0;
          }
          .secondary, ha-relative-time {
            display: block;
            color: var(--secondary-text-color);
          }
          hui-warning {
            width: 100%;
          }
          state-badge {
            flex: 0 0 40px;
            cursor: pointer;
          }
          .icon-small {
            width: auto;
          }
          .entity {
            text-align: center;
            cursor: pointer;
          }
          .entity span {
            font-size: 10px;
            color: var(--secondary-text-color);
          }
          .entities-row {
            flex-direction: row;
            display: inline-flex;
            justify-content: space-between;
            align-items: center;
          }
          .entities-row .entity {
            margin-right: 16px;
          }
          .entities-row .entity:last-of-type {
            margin-right: 0;
          }
          .entities-column {
            flex-direction: column;
            display: flex;
            align-items: flex-end;
            justify-content: space-evenly;
          }
          .entities-column .entity div {
            display: inline-block;
            vertical-align: middle;
          }`;
        }

        render() {
            return this.state.stateObj ? html`
            <state-badge
                .stateObj="${this.state.stateObj}"
                .overrideIcon="${this._config.icon}"
                .stateColor="${this._config.state_color}"
                @click="${this.onRowClick}">
            </state-badge>
            <div class="flex">
                <div class="info" @click="${this.onRowClick}">
                    ${this.state.name}
                    <div class="secondary" style="${this.state.info && this.state.info.style}">${this.renderSecondaryInfo()}</div>
                </div>
                <div class="${this._config.column ? 'entities-column' : 'entities-row'}">
                    ${this.state.entities.map(entity => this.renderEntity(entity))}
                    ${this.state.value ? html`
                    <div class="state entity" style="${this.state.style}" @click="${this.onRowClick}">
                        ${this.stateHeader && html`<span>${this.stateHeader}</span>`}
                        <div>${this.renderMainState()}</div>
                    </div>` : null}
                </div>
            </div>` : html`
            <hui-warning>
                ${this._hass.localize('ui.panel.lovelace.warning.entity_not_found', 'entity', this._config.entity)}
            </hui-warning>`;
        }

        renderMainState() {
            if (this.state.toggle) return this.renderToggle(this.state.stateObj);
            const unit = this.state.unit && !this.state.unavailable ? ` ${this.state.unit}` : null;
            return html`${this.renderValue(this.state)}${unit}`;
        }

        renderSecondaryInfo() {
            if (this.lastChanged)
                return html`<ha-relative-time datetime="${this.state.stateObj.last_changed}" .hass="${this._hass}"></ha-relative-time>`;
            if (this.state.info) {
                const name = this.state.info.name ? `${this.state.info.name} ` : null;
                const unit = this.state.info.unit && !this.state.info.unavailable ? ` ${this.state.info.unit}` : null;
                return html`${name}${this.renderValue(this.state.info)}${unit}`;
            }
        }

        renderToggle(stateObj) {
            return html`<ha-entity-toggle .stateObj="${stateObj}" .hass="${this._hass}"></ha-entity-toggle>`;
        }

        renderValue(entity) {
            if (entity.unavailable || !entity.format) return entity.value;
            if (entity.format === 'duration') return html`${this.secondsToDuration(entity.value)}`;
            if (entity.format.startsWith('precision')) {
                const precision = parseInt(entity.format.slice(-1), 10);
                return html`${parseFloat(entity.value).toFixed(precision)}`;
            }
            return html`<hui-timestamp-display .ts=${new Date(entity.value)} .format=${entity.format} .hass=${this._hass}></hui-timestamp-display>`;
        }

        renderIcon(entity) {
            return html`<state-badge class="icon-small" .stateObj="${entity.stateObj}" .overrideIcon="${entity.icon}" .stateColor="${entity.state_color}"></state-badge>`;
        }

        renderEntityValue(entity) {
            if (entity.toggle) return this.renderToggle(entity.stateObj);
            if (entity.icon !== undefined) return this.renderIcon(entity);
            const unit = entity.unit && !entity.unavailable ? ` ${entity.unit}` : null;
            return html`${this.renderValue(entity)}${unit}`;
        }

        renderEntity(entity) {
            return entity ? html`
            <div class="entity" style="${entity.style}" @click="${entity.onClick}">
                <span>${entity.name}</span>
                <div>${this.renderEntityValue(entity)}</div>
            </div>` : null;
        }

        setConfig(config) {
            if (!config.entity) throw new Error('Please define a main entity.');
            if (config.entities) {
                config.entities.map(entity => this.checkEntity(entity));
            }
            this.checkEntity(config.secondary_info);

            this.lastChanged = config.secondary_info === 'last-changed';
            this.stateHeader = config.state_header !== undefined ? config.state_header : null;
            this.onRowClick = this.getAction(config.tap_action, config.entity);

            this._config = config;
        }

        set hass(hass) {
            this._hass = hass;

            if (hass && this._config) {
                const mainStateObj = hass.states[this._config.entity];

                this.state = mainStateObj ? {
                    ...this.state,

                    stateObj: mainStateObj,
                    name: this.entityName(this._config.name, mainStateObj),
                    value: this._config.show_state !== false ? this.entityStateValue(mainStateObj) : null,
                    unit: this._config.unit === false ? null : (this._config.unit || mainStateObj.attributes.unit_of_measurement),
                    unavailable: [UNKNOWN, UNAVAILABLE].includes(mainStateObj.state),
                    toggle: this.checkToggle(this._config, mainStateObj),
                    format: this._config.format || false,
                    style: this.entityStyles(this._config),

                    entities: this._config.entities ? this._config.entities.map(entity => this.initEntity(entity, mainStateObj)) : [],
                    info: this.lastChanged ? null :
                        typeof this._config.secondary_info === 'string'
                            ? {value: this._config.secondary_info}
                            : this.initEntity(this._config.secondary_info, mainStateObj),
                } : {};
            }
        }

        checkEntity(config) {
            if (config && typeof config === 'object' && !(config.entity || config.attribute || config.icon)) {
                throw new Error(`Entity object requires at least one 'entity', 'attribute' or 'icon'.`);
            } else if (config && typeof config === 'string' && config === '') {
                throw new Error('Entity ID string must not be blank.');
            } else if (config && typeof config !== 'string' && typeof config !== 'object') {
                throw new Error('Entity config must be a valid entity ID string or entity object.');
            }
        }

        checkToggle(config, stateObj) {
            return config.toggle === true && stateObj.state && ![UNKNOWN, UNAVAILABLE].includes(stateObj.state)
        }

        initEntity(config, mainStateObj) {
            if (!config) return null;

            const entity = typeof config === 'string' ? config : config.entity;
            const stateObj = entity ? (this._hass && this._hass.states[entity]) : mainStateObj;

            if (config.hide_unavailable && (!stateObj || [UNKNOWN, UNAVAILABLE].includes(stateObj.state))) return null;

            if (!stateObj) return {value: this._hass.localize('state.default.unavailable'), unavailable: true};

            return {
                stateObj: stateObj,
                name: entity ? this.entityName(config.name, stateObj) : (config.name || null),
                value: config.attribute !== undefined
                    ? this.entityAttribute(stateObj, config.attribute)
                    : this.entityStateValue(stateObj),
                unit: config.unit === false ? null : config.attribute !== undefined ? config.unit : (config.unit || stateObj.attributes.unit_of_measurement),
                unavailable: [UNKNOWN, UNAVAILABLE].includes(config.attribute !== undefined ? stateObj.attributes[config.attribute] : stateObj.state),
                toggle: this.checkToggle(config, stateObj),
                icon: config.icon === true ? (stateObj.attributes.icon || null) : config.icon,
                format: config.format || false,
                state_color: config.state_color || false,
                style: this.entityStyles(config),
                onClick: this.getAction(config.tap_action, stateObj.entity_id),
            };
        }

        entityName(name, stateObj) {
            if (name === false) return null;
            if (name !== undefined) return name;
            return stateObj.attributes.friendly_name === undefined
                ? stateObj.entity_id.substr(stateObj.entity_id.indexOf('.') + 1).replace(/_/g, ' ')
                : stateObj.attributes.friendly_name || '';
        }

        entityAttribute(stateObj, attribute) {
            return (attribute in stateObj.attributes)
                ? stateObj.attributes[attribute]
                : this._hass.localize('state.default.unavailable');
        }

        entityStateValue(stateObj) {
            if (stateObj.state === UNKNOWN || stateObj.state === UNAVAILABLE) {
                return this._hass.localize(`state.default.${stateObj.state}`);
            }

            const domain = stateObj.entity_id.substr(0, stateObj.entity_id.indexOf('.'));
            return (
                (stateObj.attributes.device_class
                    && this._hass.localize(`component.${domain}.state.${stateObj.attributes.device_class}.${stateObj.state}`))
                || this._hass.localize(`component.${domain}.state._.${stateObj.state}`)
                || stateObj.state
            );
        }

        entityStyles(config) {
            return config.styles && typeof config.styles === 'object'
                ? Object.keys(config.styles).map(key => `${key}: ${config.styles[key]};`).join('') : '';
        }

        getAction(config, entityId) {
            if (!config || !config.action || config.action === 'more-info') {
                return () => this.fireEvent(this, 'hass-more-info', {entityId: (config && config.entity) || entityId});
            }
            if (config.action === 'none') {
                return null;
            }

            return () => {
                if (config.confirmation) {
                    this.forwardHaptic('warning');

                    if (!confirm(config.confirmation === true ? `Are you sure?` : config.confirmation)) {
                        return;
                    }
                }

                switch (config.action) {
                    case 'call-service': {
                        if (!config.service) {
                            this.forwardHaptic('failure');
                            return;
                        }
                        const [domain, service] = config.service.split('.');
                        this._hass.callService(domain, service, config.service_data);
                        this.forwardHaptic('light');
                        break;
                    }
                    case 'toggle': {
                        this.toggleEntity(entityId);
                        this.forwardHaptic('light');
                        break;
                    }
                    case 'url': {
                        if (config.url_path) {
                            window.open(config.url_path);
                        }
                        break;
                    }
                    case 'navigate': {
                        if (config.navigation_path) {
                            history.pushState(null, '', config.navigation_path);
                            this.fireEvent(window, 'location-changed', {replace: false});
                        }
                        break;
                    }
                }
            }
        }

        toggleEntity(entityId) {
            const turnOn = ["closed", "locked", "off"].includes(this._hass.states[entityId].state);
            const stateDomain = entityId.split('.')[0];
            const serviceDomain = stateDomain === "group" ? "homeassistant" : stateDomain;

            let service;
            switch (stateDomain) {
                case "lock":
                    service = turnOn ? "unlock" : "lock";
                    break;
                case "cover":
                    service = turnOn ? "open_cover" : "close_cover";
                    break;
                default:
                    service = turnOn ? "turn_on" : "turn_off";
            }
            this._hass.callService(serviceDomain, service, {entity_id: entityId});
        }

        fireEvent(node, type, detail = {}, options = {}) {
            const event = new Event(type, {
                bubbles: options.bubbles || true,
                cancelable: options.cancelable || true,
                composed: options.composed || true,
            });
            event.detail = detail;
            node.dispatchEvent(event);
        }

        forwardHaptic(type) {
            const event = new Event('haptic', {bubbles: true, cancelable: false, composed: true});
            event.detail = type;
            this.dispatchEvent(event);
        }

        secondsToDuration(sec) {
            const h = Math.floor(sec / 3600);
            const m = Math.floor((sec % 3600) / 60);
            const s = Math.floor((sec % 3600) % 60);
            const leftPad = (num) => (num < 10 ? `0${num}` : num);

            if (h > 0) return `${h}:${leftPad(m)}:${leftPad(s)}`;
            if (m > 0) return `${m}:${leftPad(s)}`;
            if (s > 0) return `${s}`;
            return null;
        }
    }

    customElements.define('multiple-entity-row', MultipleEntityRow);
})(window.LitElement || Object.getPrototypeOf(customElements.get('hui-masonry-view') || customElements.get('hui-view')));
