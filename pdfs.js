a.onclick = e => {
  e.preventDefault();
  document.getElementById('viewer').src =
    `https://${USER}.github.io/${REPO}/${PATH}/${f.name}`;
};
