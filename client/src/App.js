import React from 'react';
import './App.css';
import ReactTimeAgo from 'react-time-ago';
import axios from 'axios';

class Timer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      alarm_time: parseInt(props.alarm_time),
      created_at: parseInt(props.created_at),
      message: props.message,
      author: props.author
    };
  }

  // tick() {
  //   this.setState(state => ({
  //     seconds: state.seconds - 1
  //   }));
  // }

  // componentDidMount() {
  //   this.interval = setInterval(() => this.tick(), 1000);
  // }

  // componentWillUnmount() {
  //   clearInterval(this.interval);
  // }

  render() {
    return (
      // <div onClick={() => { this.setState(state => ({ seconds: 0 })); }}>
      <div>
        Triggers at: <ReactTimeAgo date={this.state.alarm_time*1000}/>
        <br/>Created at: {this.state.created_at*1000} //@TODO display nicely 
        <br/>Message: {this.state.message}
        <br/>Author: {this.state.author}
      </div>
    );
    //@TODO delete timers

  }
}

class App extends React.Component {
  constructor(props) {
      super(props);
      this.state = { loading: true, timers: [], error: false };
  }

  componentDidMount() {
    var self = this;
    //@TODO notifications instead of polling
    //@TODO periodical refresh
    axios.get('http://localhost:8080/timers', {timeout: 2000})
      .then(function (response) {
        self.setState(state => ({
          timers: response.data,
          loading: false
        }));
      })
      .catch(function (error) {
        self.setState(state => ({
          error: true,
          loading: false
        }));
      });
  }

  render() {
      var content;
      if (this.state.loading) {
        content = <div>Loading</div>;
      } else {
        if (this.state.error) {
          content = <div>An error has occurred.</div>;
        } else if ( this.state.timers.length === 0 ) {
            content = <div>No timers</div>;
        } else {
            const listItems = this.state.timers.map((timer) => <Timer alarm_time={timer.alarm_time} created_at={timer.created_at} message={timer.message} author={timer.author}></Timer>);

            content = <div>{listItems}</div>;
        }
      }


      return (
          <div className="App">
              <h1>Discord Bot Timers</h1>
              <div>
                  {content}
              </div>
          </div>
      );
  }
}

export default App;
