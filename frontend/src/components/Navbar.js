import { Link } from "react-router-dom";

const Navbar = () => {
  function myFunction(e) {
    e.preventDefault();
    let x = document.getElementById("top_bar");
    if (x.className === "top") {
      x.className += " mobile";
    } else {
      x.className = "top";
    }
  }

  return (
    <div id="top_bar" className="top">
      <Link className="hamburger" onClick={myFunction}>
        {" "}
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
      <div id="coffee">
        <script
          type="text/javascript"
          src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js"
          data-name="bmc-button"
          data-slug="fezcgrfkb"
          data-color="#000000"
          data-emoji=""
          data-font="Cookie"
          data-text="Buy me a coffee"
          data-outline-color="#fff"
          data-font-color="#fff"
          data-coffee-color="#fd0"
        ></script>
      </div>
    </div>
  );
};

export default Navbar;
