let nodes = [];
let connections = [];
let selectedNode = null;
const container = document.getElementById("canvas-container");

function addNode(type) {
  const id = "node_" + Date.now();
  const node = {
    id: id,
    type: type,
    prompt: type === 'start' ? "Welcome. How can I help you?" : "Press 1 or speak options.",
    x: 50 + (nodes.length * 40) % 200,
    y: 50 + (nodes.length * 40) % 200
  };
  nodes.push(node);
  renderNode(node);
}

function renderNode(node) {
  const div = document.createElement("div");
  div.className = "node";
  div.id = node.id;
  div.style.left = node.x + "px";
  div.style.top = node.y + "px";
  
  div.innerHTML = `
    <div class="node-header">${node.type}</div>
    <div class="small">${node.prompt.substring(0, 30)}...</div>
  `;
  
  // Simple drag setup
  div.onmousedown = (e) => {
    e.preventDefault();
    selectNode(node);
    let shiftX = e.clientX - div.getBoundingClientRect().left;
    let shiftY = e.clientY - div.getBoundingClientRect().top;
    
    function moveAt(pageX, pageY) {
      const parentRect = container.getBoundingClientRect();
      let x = pageX - parentRect.left - shiftX;
      let y = pageY - parentRect.top - shiftY;
      div.style.left = x + "px";
      div.style.top = y + "px";
      node.x = x;
      node.y = y;
    }
    
    function onMouseMove(event) {
      moveAt(event.pageX, event.pageY);
    }
    
    document.addEventListener('mousemove', onMouseMove);
    
    div.onmouseup = () => {
      document.removeEventListener('mousemove', onMouseMove);
      div.onmouseup = null;
    };
  };
  
  container.appendChild(div);
}

function selectNode(node) {
  selectedNode = node;
  const panel = document.getElementById("property-panel");
  panel.innerHTML = `
    <div class="row g-2">
      <div class="col-md-4">
        <label class="form-label">Node Type</label>
        <input type="text" class="form-input" value="${node.type}" disabled>
      </div>
      <div class="col-md-8">
        <label class="form-label">Prompt Statement (TTS output)</label>
        <input type="text" class="form-input" id="edit-prompt" value="${node.prompt}" oninput="updateNodePrompt(this.value)">
      </div>
    </div>
    <div class="mt-3">
      <h6>Outbound Route / Links</h6>
      <div class="input-group mb-2" style="max-width: 400px;">
        <input type="text" class="form-input form-control-sm" id="route-condition" placeholder="DTMF digit / Intent Match">
        <select class="form-input form-control-sm" id="route-target">
          ${nodes.filter(n => n.id !== node.id).map(n => `<option value="${n.id}">${n.type} (${n.id.substring(5,9)})</option>`).join('')}
        </select>
        <button class="btn btn-outline-primary btn-sm" onclick="addRoute()">Add Link</button>
      </div>
      <div id="links-list">
        ${connections.filter(c => c.from === node.id).map(c => `<span class="badge bg-secondary me-1">${c.condition} ➡️ ${c.to.substring(5,9)}</span>`).join('')}
      </div>
    </div>
  `;
}

function updateNodePrompt(val) {
  if (selectedNode) {
    selectedNode.prompt = val;
    const nodeEl = document.getElementById(selectedNode.id);
    if (nodeEl) {
      nodeEl.querySelector(".small").innerText = val.substring(0, 30) + "...";
    }
  }
}

function addRoute() {
  if (!selectedNode) return;
  const condition = document.getElementById("route-condition").value;
  const target = document.getElementById("route-target").value;
  
  if (condition && target) {
    connections.push({
      from: selectedNode.id,
      to: target,
      condition: condition
    });
    selectNode(selectedNode);
  }
}

async function saveFlow() {
  const name = prompt("Enter flow name:", "Active IVR Flow");
  if (!name) return;
  
  const res = await fetch("/api/flows", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      name: name,
      flow_json: JSON.stringify({nodes, connections}),
      is_active: 1
    })
  });
  if (res.ok) alert("Flow saved and activated successfully!");
}

function exportFlow() {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({nodes, connections}));
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", "ivr_flow.json");
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
}

function importFlow() {
  const input = document.createElement('input');
  input.type = 'file';
  input.onchange = e => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.readAsText(file,'UTF-8');
    reader.onload = readerEvent => {
      const content = JSON.parse(readerEvent.target.result);
      container.innerHTML = "";
      nodes = content.nodes || [];
      connections = content.connections || [];
      nodes.forEach(renderNode);
    }
  }
  input.click();
}
