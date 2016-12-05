import React, { Component, PropTypes } from 'react'
import Relay from 'react-relay'
import ProductList from './ProductList'
import ProductFilters from './ProductFilters'

const PAGINATE_BY = 20;


class CategoryPage extends Component {

	static propTypes = {
		attributes: PropTypes.array,
		category: PropTypes.object,
    relay: PropTypes.object
	}

  onFilterChanged = (enabled) => {
    this.props.relay.setVariables({
      attributesFilter: enabled
    })
  }

  onLoadMore = () => {
    this.props.relay.setVariables({
      count: this.props.relay.variables.count + PAGINATE_BY
    })
  }

	render() {
		const category = this.props.category;
		const attributes = this.props.attributes;

		return (
			<div className="row">
				<div className="col-md-3">
					<ProductFilters
            attributes={attributes}
            categories={category}
            onFilterChanged={this.onFilterChanged}
          />
				</div>
				<div className="col-md-9">
					<div className="row">
						<ProductList
              onLoadMore={this.onLoadMore}
              products={category.products}
            />
					</div>
				</div>		
			</div>
		)
	}
}

export default Relay.createContainer(CategoryPage, {
  initialVariables: {
    attributesFilter: [],
    count: PAGINATE_BY
  },
  fragments: {
    category: () => Relay.QL`
      fragment on CategoryType {
        id
        name
        url
        children(first: 20) {
          edges {
            node {
              id
              name
              url
            }
          }
        }
        products (first: $count, attributes: $attributesFilter) {
          ${ProductList.getFragment('products')}
        }
      }
    `,
  },
});
