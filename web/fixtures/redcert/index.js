const puppeteer = require("puppeteer");
const fs = require("fs/promises");

(async () => {
  const REDCERT_URL = "https://redcert.eu/ZertifikateDatenAnzeige.aspx";

  console.log("Start loading REDCERT website");

  const browser = await puppeteer.launch({
    headless: true,
    executablePath: "/usr/bin/chromium-browser",
    args: [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--single-process",
      "--no-zygote",
    ],
  });

  const page = await browser.newPage();

  page.setDefaultNavigationTimeout(60000);

  // load redcert site
  await page.goto(REDCERT_URL, { waitUntil: "load" });

  console.log("Page loaded");

  // click on button to switch to english
  await page.click("#ctl00_languageEnglishLinkButton");

  // prepare file download
  await page._client.send("Page.setDownloadBehavior", {
    behavior: "allow",
    downloadPath: "./downloads",
  });

  // click on file export button
  await page.click(
    "#ctl00_mainContentPlaceHolder_exportPublicZertifikatListeButton"
  );

  console.log("Start downloading REDCERT certificates");

  // reset download dir
  await fs.mkdir("./downloads", { recursive: true });

  const dir = await fs.readdir("./downloads");
  for (const file of dir) {
    await fs.rm(`./downloads/${file}`);
  }

  let file = null;
  while (file === null) {
    const dir = await fs.readdir("./downloads");

    // check if the file is there yet
    if (dir.length > 0) {
      file = dir[0];
    }

    // wait 5s
    await new Promise((resolve) => setTimeout(resolve, 5000));
  }

  console.log("Certificates downloaded:", file);

  await browser.close();
})();
