import pygame
import random
import sys
import time

pygame.init()

LEBAR_LAYAR = 600
TINGGI_LAYAR = 700
FPS = 60

PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)
ORANYE = (255, 165, 0)
BIRU = (0, 191, 255)
ABU_ABU = (105, 105, 105)
MERAH = (255, 0, 0)
KUNING = (255, 215, 0)
PINK = (255, 182, 193)
CYAN = (0, 255, 255)
HIJAU = (34, 139, 34)
COKLAT = (139, 69, 19)

layar = pygame.display.set_mode((LEBAR_LAYAR, TINGGI_LAYAR))
pygame.display.set_caption("Miauwangan")
clock = pygame.time.Clock()

font_judul = pygame.font.SysFont("Arial", 45, bold=True)
font_skor = pygame.font.SysFont("Arial", 30, bold=True)
font_gameover = pygame.font.SysFont("Arial", 50, bold=True)
font_label = pygame.font.SysFont("Arial", 18, bold=True)
font_instruksi = pygame.font.SysFont("Arial", 22)

class Kucing:
    def __init__(self):
        self.lebar = 70
        self.tinggi = 50
        self.x = (LEBAR_LAYAR // 2) - (self.lebar // 2)
        self.y = TINGGI_LAYAR - self.tinggi - 20
        
        self.kecepatan_normal = 8
        self.kecepatan_boost = 15
        self.kecepatan = self.kecepatan_normal
        self.timer_speed = 0
        
        self.warna = ORANYE
        self.rect = pygame.Rect(self.x, self.y, self.lebar, self.tinggi)
        
        self.punya_shield = False
        self.timer_shield = 0
        
        self.timer_serangan = 0
        self.cooldown_serangan = 0
        self.rect_serangan = pygame.Rect(0, 0, 0, 0)

    def gerak(self, tombol_ditekan):
        if self.timer_speed > 0:
            self.kecepatan = self.kecepatan_boost
            self.timer_speed -= 1
        else:
            self.kecepatan = self.kecepatan_normal

        if tombol_ditekan[pygame.K_LEFT] and self.x > 0:
            self.x -= self.kecepatan
        if tombol_ditekan[pygame.K_RIGHT] and self.x < LEBAR_LAYAR - self.lebar:
            self.x += self.kecepatan
            
        if tombol_ditekan[pygame.K_SPACE] and self.timer_serangan == 0 and self.cooldown_serangan == 0:
            self.timer_serangan = 15
            
        if self.timer_serangan > 0:
            self.timer_serangan -= 1
            self.rect_serangan = pygame.Rect(self.x - 20, self.y - 40, self.lebar + 40, 40)
            if self.timer_serangan == 0:
                self.cooldown_serangan = 30
        
        if self.cooldown_serangan > 0:
            self.cooldown_serangan -= 1
        
        self.rect.x = self.x
        
        if self.punya_shield:
            self.timer_shield -= 1
            if self.timer_shield <= 0:
                self.punya_shield = False

    def gambar(self, permukaan):
        if self.timer_serangan > 0:
            pygame.draw.rect(permukaan, CYAN, self.rect_serangan, border_radius=10)
            pygame.draw.line(permukaan, PUTIH, (self.rect_serangan.left + 5, self.rect_serangan.centery), (self.rect_serangan.right - 5, self.rect_serangan.centery), 4)

        if self.punya_shield:
            pygame.draw.rect(permukaan, KUNING, (self.x - 5, self.y - 5, self.lebar + 10, self.tinggi + 10), 3, border_radius=12)

        pygame.draw.rect(permukaan, self.warna, self.rect, border_radius=10)
        pygame.draw.polygon(permukaan, self.warna, [(self.x, self.y), (self.x + 15, self.y - 15), (self.x + 30, self.y)])
        pygame.draw.polygon(permukaan, self.warna, [(self.x + self.lebar, self.y), (self.x + self.lebar - 15, self.y - 15), (self.x + self.lebar - 30, self.y)])

class BendaJatuh:
    def __init__(self, warna, kecepatan, label):
        self.lebar_benda = 65  
        self.tinggi_benda = 35
        self.x = random.randint(0, LEBAR_LAYAR - self.lebar_benda)
        self.y = -50
        self.warna = warna
        self.kecepatan = kecepatan
        self.rect = pygame.Rect(self.x, self.y, self.lebar_benda, self.tinggi_benda)
        
        self.teks_permukaan = font_label.render(label, True, HITAM)
        self.teks_rect = self.teks_permukaan.get_rect()

    def turun(self):
        self.y += self.kecepatan
        self.rect.y = self.y
        self.teks_rect.center = self.rect.center

    def gambar(self, permukaan):
        pygame.draw.rect(permukaan, self.warna, self.rect, border_radius=8)
        permukaan.blit(self.teks_permukaan, self.teks_rect)

class Ikan(BendaJatuh):
    def __init__(self, tingkat_kesulitan=0):
        super().__init__(BIRU, random.randint(4 + tingkat_kesulitan, 7 + tingkat_kesulitan), "IKAN")
        self.poin = 10 

class Batu(BendaJatuh):
    def __init__(self, tingkat_kesulitan=0):
        super().__init__(ABU_ABU, random.randint(6 + tingkat_kesulitan, 10 + tingkat_kesulitan), "BATU")
        self.damage = 1 

class Hati(BendaJatuh):
    def __init__(self, tingkat_kesulitan=0):
        super().__init__(PINK, random.randint(3 + tingkat_kesulitan, 6 + tingkat_kesulitan), "NYAWA")
        self.heal = 1

class Bintang(BendaJatuh):
    def __init__(self, tingkat_kesulitan=0):
        super().__init__(KUNING, random.randint(5 + tingkat_kesulitan, 8 + tingkat_kesulitan), "SHIELD")

class Daging(BendaJatuh):
    def __init__(self, tingkat_kesulitan=0):
        super().__init__(COKLAT, random.randint(4 + tingkat_kesulitan, 7 + tingkat_kesulitan), "SPEED")

def main():
    status_game = "MENU"
    
    player = Kucing()
    daftar_ikan = []
    daftar_batu = []
    daftar_hati = []     
    daftar_bintang = []  
    daftar_daging = []   

    skor = 0
    nyawa = 3

    waktu_muncul_ikan = 0
    waktu_muncul_batu = 0
    waktu_muncul_hati = 0     
    waktu_muncul_bintang = 0  
    waktu_muncul_daging = 0  

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if status_game == "MENU":
                    if event.key == pygame.K_RETURN:
                        status_game = "MAIN"
                
                elif status_game == "GAMEOVER":
                    if event.key == pygame.K_RETURN:
                        player = Kucing()
                        daftar_ikan.clear()
                        daftar_batu.clear()
                        daftar_hati.clear()
                        daftar_bintang.clear()
                        daftar_daging.clear() 
                        skor = 0
                        nyawa = 3
                        waktu_muncul_ikan = 0
                        waktu_muncul_batu = 0
                        waktu_muncul_hati = 0     
                        waktu_muncul_bintang = 0  
                        waktu_muncul_daging = 0   
                        status_game = "MAIN"
                    
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        layar.fill(PUTIH)

        if status_game == "MENU":
            teks_judul = font_judul.render("MIAUWANGAN", True, ORANYE)
            
            instruksi = [
                "CARA BERMAIN:",
                "- Gunakan Panah Kiri (<-) dan Kanan (->) untuk bergerak.",
                "- Tekan SPASI untuk menebas/menghancurkan BATU.",
                "- Tangkap IKAN (Biru) untuk mendapatkan skor.",
                "- Hindari BATU (Abu-abu) agar nyawa tidak berkurang.",
                "- Tangkap NYAWA (Pink) untuk menambah darah.",
                "- Tangkap SHIELD (Kuning) untuk kebal selama 5 detik.",
                "- Tangkap SPEED (Coklat) untuk lari cepat selama 5 detik."
            ]
            
            teks_mulai = font_skor.render("Tekan [ENTER] Untuk Mulai", True, HIJAU)
            
            layar.blit(teks_judul, (LEBAR_LAYAR//2 - teks_judul.get_width()//2, 80))
            
            y_offset = 180
            for baris in instruksi:
                teks_baris = font_instruksi.render(baris, True, HITAM)
                layar.blit(teks_baris, (50, y_offset))
                y_offset += 35
                
            layar.blit(teks_mulai, (LEBAR_LAYAR//2 - teks_mulai.get_width()//2, 500))

        elif status_game == "MAIN":
            tombol = pygame.key.get_pressed()
            player.gerak(tombol)

            level = skor // 50 
            batas_level = min(level, 10) 

            waktu_muncul_ikan += 1
            batas_spawn_ikan = max(15, 40 - (batas_level * 2))
            if waktu_muncul_ikan > batas_spawn_ikan: 
                daftar_ikan.append(Ikan(batas_level)) 
                waktu_muncul_ikan = 0

            waktu_muncul_batu += 1
            batas_spawn_batu = max(15, 60 - (batas_level * 4))
            if waktu_muncul_batu > batas_spawn_batu:
                daftar_batu.append(Batu(batas_level)) 
                waktu_muncul_batu = 0

            waktu_muncul_hati += 1
            if waktu_muncul_hati > 600: 
                daftar_hati.append(Hati(batas_level))
                waktu_muncul_hati = 0
                
            waktu_muncul_bintang += 1
            if waktu_muncul_bintang > 800:
                daftar_bintang.append(Bintang(batas_level))
                waktu_muncul_bintang = 0
                
            waktu_muncul_daging += 1
            if waktu_muncul_daging > 750:
                daftar_daging.append(Daging(batas_level))
                waktu_muncul_daging = 0

            for ikan in daftar_ikan[:]:
                ikan.turun()
                if player.rect.colliderect(ikan.rect):
                    skor += ikan.poin
                    daftar_ikan.remove(ikan)
                elif ikan.y > TINGGI_LAYAR:
                    daftar_ikan.remove(ikan)

            for batu in daftar_batu[:]:
                batu.turun()
                
                if player.timer_serangan > 0 and player.rect_serangan.colliderect(batu.rect):
                    daftar_batu.remove(batu)
                    skor += 5 
                    continue 
                
                if player.rect.colliderect(batu.rect):
                    if not player.punya_shield:
                        nyawa -= batu.damage
                        if nyawa <= 0:
                            status_game = "GAMEOVER"
                    daftar_batu.remove(batu)
                elif batu.y > TINGGI_LAYAR:
                    daftar_batu.remove(batu)

            for hati in daftar_hati[:]:
                hati.turun()
                if player.rect.colliderect(hati.rect):
                    nyawa = min(nyawa + hati.heal, 5) 
                    daftar_hati.remove(hati)
                elif hati.y > TINGGI_LAYAR:
                    daftar_hati.remove(hati)
                    
            for bintang in daftar_bintang[:]:
                bintang.turun()
                if player.rect.colliderect(bintang.rect):
                    player.punya_shield = True
                    player.timer_shield = 300 
                    daftar_bintang.remove(bintang)
                elif bintang.y > TINGGI_LAYAR:
                    daftar_bintang.remove(bintang)
                    
            for daging in daftar_daging[:]:
                daging.turun()
                if player.rect.colliderect(daging.rect):
                    player.timer_speed = 300
                    daftar_daging.remove(daging)
                elif daging.y > TINGGI_LAYAR:
                    daftar_daging.remove(daging)

            player.gambar(layar)
            for ikan in daftar_ikan: ikan.gambar(layar)
            for batu in daftar_batu: batu.gambar(layar)
            for hati in daftar_hati: hati.gambar(layar)
            for bintang in daftar_bintang: bintang.gambar(layar)
            for daging in daftar_daging: daging.gambar(layar) 

            teks_skor = font_skor.render(f"Skor: {skor}", True, HITAM)
            teks_nyawa = font_skor.render(f"Nyawa: {nyawa}", True, MERAH)
            teks_level = font_skor.render(f"Level: {min((skor // 50) + 1, 10)}", True, BIRU)
            
            layar.blit(teks_skor, (10, 10))
            layar.blit(teks_nyawa, (10, 40))
            layar.blit(teks_level, (10, 70))
            
            y_pos_hud = 100
            
            if player.punya_shield:
                detik_sisa = player.timer_shield // 60
                teks_shield = font_skor.render(f"Shield: {detik_sisa}s", True, KUNING)
                layar.blit(teks_shield, (10, y_pos_hud))
                y_pos_hud += 30 
                
            if player.timer_speed > 0:
                detik_speed = player.timer_speed // 60
                teks_speed = font_skor.render(f"Speed: {detik_speed}s", True, COKLAT)
                layar.blit(teks_speed, (10, y_pos_hud))
        
        elif status_game == "GAMEOVER":
            teks_go = font_gameover.render("GAME OVER", True, MERAH)
            teks_skor_akhir = font_skor.render(f"Skor Akhir Kamu: {skor}", True, HITAM)
            teks_restart = font_instruksi.render("Tekan [ENTER] untuk Main Lagi", True, HIJAU)
            teks_exit = font_instruksi.render("Tekan [ESC] untuk Keluar", True, ABU_ABU)
            
            layar.blit(teks_go, (LEBAR_LAYAR//2 - teks_go.get_width()//2, TINGGI_LAYAR//2 - 80))
            layar.blit(teks_skor_akhir, (LEBAR_LAYAR//2 - teks_skor_akhir.get_width()//2, TINGGI_LAYAR//2 - 10))
            layar.blit(teks_restart, (LEBAR_LAYAR//2 - teks_restart.get_width()//2, TINGGI_LAYAR//2 + 60))
            layar.blit(teks_exit, (LEBAR_LAYAR//2 - teks_exit.get_width()//2, TINGGI_LAYAR//2 + 100))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()