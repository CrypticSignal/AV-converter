import { Link } from "react-router-dom";
import gitHubLogo from "../images/GitHub-Mark-Light-32px.png";

const Navbar = () => {
  function myFunction(e) {
    e.preventDefault();
    let x = document.getElementById("subdomains");
    if (x.className === "top") {
      x.className += " mobile";
    } else {
      x.className = "top";
    }
  }

  return (
    <div id="subdomains" className="top">
      <Link to="/" className="hamburger" onClick={myFunction}>
        <i className="fa fa-bars"></i>
      </Link>
      <Link to="/">Home</Link>
      <Link to="about">About</Link>
      <Link to="filetypes">Filetypes</Link>
      <Link to="yt">YT downloader</Link>
      <Link
        to="game"
        onClick={() => {
          window.location.href = "game";
        }}
      >
        Game
      </Link>

      <a href="https://github.com/CrypticSignal/av-converter" id="github_link">
        <img src={gitHubLogo} />
      </a>
    </div>
  );
};

export default Navbar;
