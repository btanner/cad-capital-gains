import React from 'react';
import './App.css';
import { Table, Checkbox, Icon, Button, Tab } from 'semantic-ui-react';

const tickers = [
  { menuItem: 'ANET', render: () => <Tab.Pane>ANET</Tab.Pane> },
  { menuItem: 'ITOT', render: () => <Tab.Pane>ITOT</Tab.Pane> },
]
function App() {
  return (
    <Tab
      menu={{ fluid: true, vertical: true }}
      panes={tickers}
    />
//    <Table celled selectable>
//      <Table.Header>
//        <Table.Row>
//          <Table.HeaderCell />
//          <Table.HeaderCell>Date</Table.HeaderCell>
//          <Table.HeaderCell>Action</Table.HeaderCell>
//          <Table.HeaderCell>Description</Table.HeaderCell>
//          <Table.HeaderCell>Ticker</Table.HeaderCell>
//          <Table.HeaderCell>Quantity</Table.HeaderCell>
//          <Table.HeaderCell>Price</Table.HeaderCell>
//          <Table.HeaderCell>Commission</Table.HeaderCell>
//        </Table.Row>
//      </Table.Header>
//
//      <Table.Body>
//        <Table.Row positive>
//          <Table.Cell>
//            <Checkbox />
//          </Table.Cell>
//          <Table.Cell>September 14, 2013</Table.Cell>
//          <Table.Cell>BUY</Table.Cell>
//          <Table.Cell>ESPP Purchase</Table.Cell>
//          <Table.Cell>ANET</Table.Cell>
//          <Table.Cell>100</Table.Cell>
//          <Table.Cell>$59.99</Table.Cell>
//          <Table.Cell>-</Table.Cell>
//        </Table.Row>
//        <Table.Row negative>
//          <Table.Cell>
//            <Checkbox />
//          </Table.Cell>
//          <Table.Cell>September 15, 2013</Table.Cell>
//          <Table.Cell>SELL</Table.Cell>
//          <Table.Cell>ESPP Purchase</Table.Cell>
//          <Table.Cell>ANET</Table.Cell>
//          <Table.Cell>100</Table.Cell>
//          <Table.Cell>$59.99</Table.Cell>
//          <Table.Cell>-</Table.Cell>
//        </Table.Row>
//      </Table.Body>
//
//      <Table.Footer fullWidth>
//        <Table.Row>
//          <Table.HeaderCell colSpan='8'>
//            <Button disabled size='small'>Delete transactions</Button>
//            <Button
//              floated='right'
//              icon
//              labelPosition='left'
//              primary
//              size='small'
//            >
//              <Icon name='add' />Add Transaction
//            </Button>
//          </Table.HeaderCell>
//        </Table.Row>
//      </Table.Footer>
//    </Table>
  );
}

export default App;
