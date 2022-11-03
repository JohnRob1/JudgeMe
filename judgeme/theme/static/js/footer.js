const footerTemplate = document.createElement("template");
footerTemplate.innerHTML = `

<style>
<style>
.container {
    position: fixed;
    bottom: 0px
    padding: 6rem
}
.column {
    display: flex;
    flex-direction: column;
}
.page-footer {

    
}

</style>
<header class="container">
    <div class="column">
        <a href="../">
            <p class="text-4xl title">JudgeMe</p>
        </a>

        <div class="flex space-x-2">
            <button onclick="location.href = '../about/'">about</button>
            <!-- <p>terms</p> -->
        </div>
    </div>
</header>
`;

class Footer extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
        this.shadowRoot.appendChild(footerTemplate.content.cloneNode(true));
    }
}
window.customElements.define("page-footer", Footer);
