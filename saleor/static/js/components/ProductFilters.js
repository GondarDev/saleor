import React, { Component, PropTypes } from 'react'
import Relay from 'react-relay';


class ProductFilters extends Component {

  static propTypes = {
    attributes: PropTypes.array,
    onFilterChanged: PropTypes.func.isRequired,
    urlParams: PropTypes.func.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      filters: {}
    };
  }

  onClick = (attribute, value) => {
    const attrValue = `${attribute}:${value}`;
    this.setState({
      filters: Object.assign(
        this.state.filters,
        {[attrValue]: !this.state.filters[attrValue]})
    });
    const enabled = Object.keys(this.state.filters).filter(key => this.state.filters[key] === true);
    this.props.onFilterChanged(enabled);
  
  }

  render() {
    const { attributes } = this.props;
    return (
      <div className="attributes">
        {attributes && (attributes.map((attribute) => {
          return (
            <div key={attribute.id} className={attribute.name}>
              <ul>
                <h3>{attribute.display}</h3>
                {attribute.values.map((value) => {
                  return (
                    <li key={value.id} className="item">
                        <label>
                          <input id={'attr' + attribute.pk + value.pk} type="checkbox" value="" onClick={() => this.onClick(attribute.pk, value.pk)} />
                          {value.display}
                        </label>
                    </li>
                  )
                })}
              </ul>
            </div>
          )
        }))}
      </div>
    )
  }
}

export default Relay.createContainer(ProductFilters, {
  fragments: {
    attributes: () => Relay.QL`
      fragment on ProductAttributeType @relay(plural: true) {
        id
        pk
        name
        display
        values {
          id
          pk
          display
          color
        }
      }
    `,
  },
});
