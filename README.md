# Aurelia - League of Legends iÃ§in Zahmetsiz Skin YÃ¶netimi

<div align="center">

  <img src="./assets/icon.png" alt="Aurelia Icon" width="128" height="128">

[![Installer](https://img.shields.io/badge/Installer-Windows-32A832)](https://github.com/shazeus/Aurelia/releases/latest) [![Fork](https://img.shields.io/badge/Fork-shazeus-32A832)](https://github.com/shazeus/Aurelia) [![Sponsors](https://img.shields.io/badge/GitHub-Sponsors-C03030?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/shazeus) [![Discord](https://img.shields.io/discord/1490473857075642621?color=32A832&logo=discord&logoColor=white&label=Discord)](https://discord.com/invite/aureliaskins) [![Lisans](https://img.shields.io/badge/Lisans-MIT-C03030)](LICENSE) [![Ä°ndirmeler](https://img.shields.io/github/downloads/shazeus/Aurelia/total?color=32A832&label=Fork%20Indirmeleri)](https://github.com/shazeus/Aurelia/releases/latest)

</div>

---

## Genel BakÄ±ÅŸ

Bu depo, **shazeus/Aurelia** forkudur. Forkun amacÄ± Aurelia'un mevcut Ã§alÄ±ÅŸma akÄ±ÅŸÄ±nÄ± korurken paketleme, gÃ¶rÃ¼nen proje linkleri, League Client iÃ§i panel metinleri, fork notlarÄ± ve gÃ¼ncelleme kaynaÄŸÄ± gibi fork sahibine ait kÄ±sÄ±mlarÄ± temiz hale getirmektir.

Aurelia, League of Legends iÃ§in aÃ§Ä±k kaynaklÄ± bir skin yÃ¶netim aracÄ±dÄ±r. Uygulama sistem tepsisinde Ã§alÄ±ÅŸÄ±r, ÅŸampiyon seÃ§imi sÄ±rasÄ±nda seÃ§ilen skinleri takip eder ve oyun yÃ¼klenirken yerel gÃ¶rÃ¼ntÃ¼ varlÄ±klarÄ±nÄ± uygular.

Aurelia, [Pengu Loader](https://github.com/Tariolle/ROSE-Pengu) altyapÄ±sÄ±nÄ± kullanarak League Client iÃ§ine JavaScript eklentileri entegre eder. Proje yerel model/doku gÃ¶rÃ¼nÃ¼m deÄŸiÅŸkenleriyle Ã§alÄ±ÅŸÄ±r; aÄŸ verisini, bellek durumunu veya oynanÄ±ÅŸ mekaniklerini manipÃ¼le etmeyi hedeflemez ve rekabet avantajÄ± sunmaz.

## Bu Forkta YapÄ±lan GeliÅŸtirmeler

- README, fork kullanÄ±cÄ±larÄ± iÃ§in TÃ¼rkÃ§e ve daha aÃ§Ä±k hale getirildi.
- README, installer metadata, plugin metadata, sistem tepsisi baÅŸlÄ±klarÄ± ve League Client iÃ§indeki SettingsPanel GitHub linkleri `shazeus/Aurelia` forkuna yÃ¶nlendirildi.
- [FORK_NOTES.md](FORK_NOTES.md) eklendi; forkta hangi alanlarÄ±n Ã¶zelleÅŸtirildiÄŸi ve runtime akÄ±ÅŸa dokunulmadÄ±ÄŸÄ± ayrÄ±ca belgelendi.
- Launcher updater artÄ±k varsayÄ±lan olarak `shazeus/Aurelia` release'lerini kontrol eder.
- Ã–zel build ve test senaryolarÄ± iÃ§in updater release kaynaÄŸÄ± `AURELIA_RELEASE_REPO` veya `AURELIA_RELEASE_API` ortam deÄŸiÅŸkenleriyle deÄŸiÅŸtirilebilir.
- Updater release kaynaÄŸÄ± iÃ§in kÃ¼Ã§Ã¼k regresyon testleri eklendi.
- League Client iÃ§indeki SettingsPanel'e `Aurelia` kimlik kartÄ±, canlÄ± ayar Ã¶zeti ve daha dÃ¼zenli aksiyon butonlarÄ± eklendi.
- ChromaWheel ve FormsWheel panellerine seÃ§enek sayacÄ±, kÄ±sa kullanÄ±m metni, Aurelia baÅŸlÄ±ÄŸÄ± ve klavye ile seÃ§ilebilir buton etiketleri eklendi.
- Party Mode panel baÅŸlÄ±ÄŸÄ± ve aÃ§Ä±klamasÄ± fork kimliÄŸiyle daha anlaÅŸÄ±lÄ±r hale getirildi.

## Mimari

Aurelia Ã¼Ã§ ana parÃ§adan oluÅŸur:

### Python Backend

- **LCU API Entegrasyonu**: League Client Update (LCU) API ile iletiÅŸim kurar.
- **Skin Uygulama AkÄ±ÅŸÄ±**: Riot Vanguard ile uyumlu olacak ÅŸekilde skin uygulama sÃ¼recini yÃ¶netir.
- **WebSocket KÃ¶prÃ¼sÃ¼**: Frontend eklentileriyle anlÄ±k iletiÅŸim kurmak iÃ§in WebSocket sunucusu Ã§alÄ±ÅŸtÄ±rÄ±r.
- **Skin YÃ¶netimi**: Skin dosyalarÄ±nÄ± [LeagueSkins deposundan](https://github.com/Alban1911/LeagueSkins) indirir ve dÃ¼zenler.
- **Party Mode**: AynÄ± lobideki arkadaÅŸlar arasÄ±nda skin seÃ§imlerini Cloudflare WebSocket relay Ã¼zerinden paylaÅŸÄ±r.
- **Oyun Ä°zleme**: Oyun durumunu, ÅŸampiyon seÃ§imi fazlarÄ±nÄ± ve loadout geri sayÄ±mÄ±nÄ± takip eder.
- **Otomatik GÃ¼ncelleyici**: GitHub release'lerini kontrol eder ve uygun gÃ¼ncellemeyi kullanÄ±cÄ±ya sunar.
- **Analitik**: YapÄ±landÄ±rÄ±labilir arka plan pingleriyle benzersiz kullanÄ±cÄ± sayÄ±mÄ±nÄ± takip eder.

### Cloudflare Workers

- **aurelia-party-relay**: Party odalarÄ±nÄ± yÃ¶neten Durable Object tabanlÄ± WebSocket relay servisidir. Oda baÅŸÄ±na en fazla 10 Ã¼yeyi destekler.

### Pengu Loader Eklentileri

- **ROSE-UI**: Åampiyon seÃ§imindeki kilitli skin Ã¶nizlemelerini aÃ§arak hover etkileÅŸimlerini etkinleÅŸtirir.
- **ROSE-SkinMonitor**: SeÃ§ili skin adÄ±nÄ± takip eder ve Python backend'e WebSocket ile iletir.
- **ROSE-CustomWheel**: Hover edilen skinler iÃ§in mod metadata bilgisini gÃ¶sterir ve mods klasÃ¶rÃ¼ne hÄ±zlÄ± eriÅŸim saÄŸlar.
- **ROSE-ChromaWheel**: Her chroma varyantÄ±nÄ± seÃ§mek iÃ§in geliÅŸmiÅŸ chroma arayÃ¼zÃ¼ sunar.
- **ROSE-FormsWheel**: Birden fazla forma sahip skinler iÃ§in Ã¶zel form seÃ§im arayÃ¼zÃ¼ saÄŸlar.
- **ROSE-SettingsPanel**: League Client iÃ§inden eriÅŸilebilen Aurelia ayar panelidir.
- **ROSE-RandomSkin**: Rastgele skin seÃ§imi Ã¶zelliÄŸini saÄŸlar.
- **ROSE-HistoricMode**: Her ÅŸampiyon iÃ§in son kullanÄ±lan skine hÄ±zlÄ± eriÅŸim verir.
- **ROSE-PartyMode**: Lobi ve ÅŸampiyon seÃ§iminde skin paylaÅŸÄ±mÄ±, baÄŸlÄ± kiÅŸiler ve arkadaÅŸ seÃ§imlerini gÃ¶steren paneli saÄŸlar.
- **ROSE-Jade**: Client iÃ§in border, arka plan, banner, ikon, unvan ve win/loss gÃ¶rÃ¼nÃ¼m Ã¶zelleÅŸtirmeleri sunar.

## NasÄ±l Ã‡alÄ±ÅŸÄ±r?

1. Aurelia aÃ§Ä±lÄ±ÅŸ sÄ±rasÄ±nda **[Pengu Loader](https://github.com/Tariolle/ROSE-Pengu)** entegrasyonunu baÅŸlatÄ±r.
2. `ROSE-SkinMonitor`, ÅŸampiyon seÃ§iminde hover edilen skin bilgisini algÄ±lar.
3. Python backend, gelen seÃ§imi ve oyun fazÄ±nÄ± takip eder.
4. Oyun yÃ¼klenirken seÃ§ilen skinin yerel varlÄ±klarÄ± uygulanÄ±r.
5. Skin yalnÄ±zca yerel gÃ¶rÃ¼nÃ¼m olarak yÃ¼klenir; oynanÄ±ÅŸ etkilenmez.

## Ã–zellikler

- **AkÄ±llÄ± Uygulama**: Zaten sahip olunan skinleri gereksiz yere uygulamamaya Ã§alÄ±ÅŸÄ±r.
- **Ã‡oklu Dil DesteÄŸi**: FarklÄ± League Client dilleriyle Ã§alÄ±ÅŸacak ÅŸekilde tasarlanmÄ±ÅŸtÄ±r.
- **ModÃ¼ler Plugin YapÄ±sÄ±**: UI ve istemci davranÄ±ÅŸlarÄ± Pengu Loader eklentileriyle ayrÄ±lmÄ±ÅŸtÄ±r.
- **Fork Dostu GÃ¼ncelleme**: Bu fork, gÃ¼ncellemeleri `shazeus/Aurelia` release'lerinden kontrol eder.
- **Test Edilebilir Release KaynaÄŸÄ±**: `AURELIA_RELEASE_REPO=owner/repo` veya `AURELIA_RELEASE_API=https://...` ile updater hedefi deÄŸiÅŸtirilebilir.
- **AÃ§Ä±k Kaynak**: Kod okunabilir, incelenebilir ve fork Ã¼zerinden geliÅŸtirilebilir.

## Gereksinimler

- **Windows 10/11**
- **League of Legends** kurulu olmalÄ±dÄ±r.
- **Injection DLL**: KullanÄ±cÄ±nÄ±n kendi imzalÄ± DLL dosyasÄ±nÄ± saÄŸlamasÄ± gerekir.

### DLL Gereksinimi

DMCA kÄ±sÄ±tlamalarÄ± nedeniyle Aurelia injection DLL dosyasÄ±nÄ± daÄŸÄ±tmaz. KullanÄ±cÄ± bu dosyayÄ± yetkili bir kaynaktan edinmeli ve kendi kod imzalama sertifikasÄ± ile imzalamalÄ±dÄ±r.

Ä°lk aÃ§Ä±lÄ±ÅŸta Aurelia gerekli klasÃ¶rÃ¼ aÃ§ar ve kullanÄ±cÄ±dan ilgili dosyayÄ± yerleÅŸtirmesini ister.

## Kurulum

1. En gÃ¼ncel fork installer dosyasÄ±nÄ± [Releases](https://github.com/shazeus/Aurelia/releases/latest) sayfasÄ±ndan indirin.
2. Installer'Ä± YÃ¶netici olarak Ã§alÄ±ÅŸtÄ±rÄ±n.
3. Aurelia'u BaÅŸlat MenÃ¼sÃ¼ veya masaÃ¼stÃ¼ kÄ±sayolundan aÃ§Ä±n.

## Fork AyarlarÄ±

Updater varsayÄ±lan olarak bu fork release'lerini kullanÄ±r:

```powershell
https://github.com/shazeus/Aurelia/releases/latest
```

Test veya Ã¶zel build iÃ§in kaynak deÄŸiÅŸtirme:

```powershell
$env:AURELIA_RELEASE_REPO = "kullanici/Aurelia"
```

Tam API URL'i vermek iÃ§in:

```powershell
$env:AURELIA_RELEASE_API = "https://api.github.com/repos/kullanici/Aurelia/releases/latest"
```

## KatkÄ±

GeliÅŸtirme kurulumu ve proje yapÄ±sÄ± iÃ§in [CONTRIBUTING.md](CONTRIBUTING.md) dosyasÄ±na bakÄ±n.

Fork Ã¼zerinde Ã§alÄ±ÅŸÄ±rken:

- Runtime injection akÄ±ÅŸÄ±nÄ± deÄŸiÅŸtiren commitleri ayrÄ± tutun.
- Upstream ile karÅŸÄ±laÅŸtÄ±rmasÄ± kolay, kÃ¼Ã§Ã¼k ve net commitler tercih edin.
- League Client entegrasyonuna dokunmadan Ã¶nce upstream deÄŸiÅŸikliklerini kontrol edin.

## Yasal UyarÄ±

Bu proje Riot Games tarafÄ±ndan desteklenmez ve Riot Games ile resmi bir baÄŸlantÄ±sÄ± yoktur. Riot Games ve ilgili tÃ¼m markalar Riot Games, Inc. ÅŸirketinin ticari markalarÄ± veya tescilli markalarÄ±dÄ±r.

Custom skin kullanÄ±mÄ±nda sorumluluk kullanÄ±cÄ±ya aittir. Oyun iÃ§inde skin araÃ§larÄ±nÄ± tartÄ±ÅŸmayÄ±n veya reklamÄ±nÄ± yapmayÄ±n.

## Destek

Upstream Aurelia topluluÄŸunu desteklemek isterseniz:

[GitHub Sponsors](https://github.com/sponsors/shazeus)

---

**Aurelia** - _League, unlocked._

