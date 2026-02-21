/**
 * 프로필과 뱃지 시스템 JavaScript 통합 코드
 * 기존 test-timeline.html에 추가할 함수들
 */

// === 전역 변수 ===
const CURRENT_USER_ID = 'user123'; // 실제로는 로그인 시스템에서 가져올 값
const API_BASE_URL = 'http://localhost:8000'; // 백엔드 API 베이스 URL

// === 프로필 관련 함수들 ===

/**
 * 사용자 프로필 로딩 (뱃지 포함)
 */
async function loadUserProfile(userId = CURRENT_USER_ID) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/profile/${userId}`);
        const result = await response.json();
        
        if (result.success) {
            const user = result.user;
            window.currentUserProfile = user;
            
            // UI 업데이트
            updateProfileUI(user);
            loadUserBadges(user.badges);
            
            return user;
        } else {
            console.error('프로필 로딩 실패:', result.message);
            return null;
        }
    } catch (error) {
        console.error('프로필 로딩 오류:', error);
        
        // 오류 시 기본 프로필 생성
        const defaultProfile = {
            user_id: userId,
            name: '김투자',
            bio: '10년차 개미투자자, 장기투자 선호',
            investment_style: '가치투자자',
            followers_count: 156,
            following_count: 23,
            posts_count: 47,
            badges: []
        };
        
        updateProfileUI(defaultProfile);
        return defaultProfile;
    }
}

/**
 * 프로필 UI 업데이트
 */
function updateProfileUI(user) {
    // 기본 정보 업데이트
    const nameEl = document.getElementById('myName');
    const bioEl = document.getElementById('myBio');
    const avatarEl = document.getElementById('myAvatar');
    const styleEl = document.getElementById('myInvestmentStyle');
    const followersEl = document.getElementById('myFollowers');
    const followingEl = document.getElementById('myFollowing');
    const postsEl = document.getElementById('myPosts');
    
    if (nameEl) nameEl.textContent = user.name;
    if (bioEl) bioEl.textContent = user.bio || '소개를 추가해주세요';
    if (avatarEl) avatarEl.textContent = user.name ? user.name.charAt(0) : '김';
    if (followersEl) followersEl.textContent = user.followers_count || 0;
    if (followingEl) followingEl.textContent = user.following_count || 0;
    if (postsEl) postsEl.textContent = user.posts_count || 0;
    
    // 투자성향 업데이트
    if (styleEl && user.investment_style) {
        const styleEmojis = {
            '가치투자자': '🎯',
            '모멘텀투자자': '🚀',
            '단타': '⚡',
            '스윙': '🔄',
            '배당투자자': '💰',
            '인덱스투자자': '📊',
            '비트코이너': '₿'
        };
        const emoji = styleEmojis[user.investment_style] || '🎯';
        styleEl.textContent = `${emoji} ${user.investment_style}`;
        styleEl.className = 'investment-style';
    }
}

/**
 * 사용자 뱃지 로딩 및 표시
 */
function loadUserBadges(badges = []) {
    const badgesContainer = document.getElementById('myBadges');
    const noBadgesEl = document.getElementById('noBadges');
    
    if (!badgesContainer) return;
    
    if (!badges || badges.length === 0) {
        badgesContainer.innerHTML = '';
        if (noBadgesEl) noBadgesEl.style.display = 'block';
        return;
    }
    
    if (noBadgesEl) noBadgesEl.style.display = 'none';
    
    const badgesHTML = badges.map(badge => `
        <div class="badge ${badge.rarity}" title="${badge.description}">
            <span class="badge-icon">${badge.icon}</span>
            <span class="badge-name">${badge.name}</span>
        </div>
    `).join('');
    
    badgesContainer.innerHTML = badgesHTML;
}

/**
 * 프로필 수정 함수 (백엔드 API 연동)
 */
async function saveProfile() {
    const name = document.getElementById('editName').value.trim();
    const bio = document.getElementById('editBio').value.trim();
    const investmentStyle = document.getElementById('editInvestmentStyle').value;
    
    if (!name) {
        alert('이름을 입력해주세요.');
        return;
    }
    
    if (!investmentStyle) {
        alert('투자성향을 선택해주세요.');
        return;
    }
    
    const profileData = {
        name: name,
        bio: bio,
        investment_style: investmentStyle
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/profile/${CURRENT_USER_ID}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profileData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 현재 프로필 업데이트
            window.currentUserProfile = { 
                ...window.currentUserProfile, 
                ...result.user 
            };
            
            // UI 업데이트
            updateProfileUI(window.currentUserProfile);
            
            closeModal('editProfileModal');
            alert('프로필이 저장되었습니다!');
            
        } else {
            alert(`프로필 저장 실패: ${result.message}`);
        }
        
    } catch (error) {
        console.error('프로필 저장 오류:', error);
        alert('프로필 저장 중 오류가 발생했습니다.');
    }
}

/**
 * 프로필 수정 모달 열기 (데이터 로딩 포함)
 */
function editProfile() {
    // 현재 프로필 데이터를 수정 폼에 로딩
    const currentProfile = window.currentUserProfile || {};
    
    const nameInput = document.getElementById('editName');
    const bioInput = document.getElementById('editBio');
    const styleInput = document.getElementById('editInvestmentStyle');
    
    if (nameInput) nameInput.value = currentProfile.name || '김투자';
    if (bioInput) bioInput.value = currentProfile.bio || '';
    if (styleInput) styleInput.value = currentProfile.investment_style || '가치투자자';
    
    document.getElementById('editProfileModal').classList.add('active');
}

// === 뱃지 시스템 관련 함수들 ===

/**
 * 기본 뱃지 초기화 (서버에서)
 */
async function initializeDefaultBadges() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/badges/initialize`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`기본 뱃지 초기화 완료: ${result.created_count}개 생성`);
        } else {
            console.error('뱃지 초기화 실패:', result.message);
        }
        
    } catch (error) {
        console.error('뱃지 초기화 오류:', error);
    }
}

/**
 * 모든 뱃지 목록 조회
 */
async function getAllBadges() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/badges`);
        const result = await response.json();
        
        if (result.success) {
            return result.badges;
        } else {
            console.error('뱃지 조회 실패:', result.message);
            return [];
        }
        
    } catch (error) {
        console.error('뱃지 조회 오류:', error);
        return [];
    }
}

/**
 * 사용자에게 뱃지 부여 (테스트용)
 */
async function grantBadgeToUser(userId, badgeName, reason = '') {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/${userId}/badges`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                badge_name: badgeName,
                reason: reason
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`뱃지 부여 성공: ${badgeName}`);
            
            // 프로필 새로고침
            await loadUserProfile(userId);
            
        } else {
            console.error('뱃지 부여 실패:', result.message);
        }
        
    } catch (error) {
        console.error('뱃지 부여 오류:', error);
    }
}

// === 프로필 탭 초기화 함수 ===

/**
 * 프로필 탭이 활성화될 때 호출되는 함수
 */
async function loadProfileTab() {
    console.log('프로필 탭 로딩 시작...');
    
    // 프로필 데이터 로딩
    await loadUserProfile(CURRENT_USER_ID);
    
    // 포트폴리오 관리 데이터 로딩
    loadPortfolioManagement();
    
    // 팔로잉 데이터 로딩
    loadFollowingList();
    
    console.log('프로필 탭 로딩 완료');
}

/**
 * 기존 switchTab 함수를 확장하여 프로필 탭 로딩 추가
 */
function switchTabExtended(tabName) {
    // 기존 탭 전환 로직...
    
    // 프로필 탭인 경우 추가 로딩
    if (tabName === 'profile') {
        loadProfileTab();
    }
}

// === 초기화 함수들 ===

/**
 * 프로필과 뱃지 시스템 초기화
 */
async function initializeProfileAndBadges() {
    console.log('프로필 & 뱃지 시스템 초기화 시작...');
    
    try {
        // 기본 뱃지 초기화
        await initializeDefaultBadges();
        
        // 현재 사용자 프로필 로딩
        await loadUserProfile(CURRENT_USER_ID);
        
        console.log('프로필 & 뱃지 시스템 초기화 완료');
        
    } catch (error) {
        console.error('초기화 실패:', error);
    }
}

// === 테스트 함수들 ===

/**
 * 테스트용 뱃지 부여 함수
 */
function testGrantBadges() {
    console.log('테스트 뱃지 부여 시작...');
    
    // 신규 회원 뱃지 부여
    grantBadgeToUser(CURRENT_USER_ID, '신규 회원', '가입 축하!');
    
    // 투자성향에 따른 뱃지 부여
    setTimeout(() => {
        if (window.currentUserProfile?.investment_style === '비트코이너') {
            grantBadgeToUser(CURRENT_USER_ID, '비트코이너', '암호화폐 투자자 인증');
        } else if (window.currentUserProfile?.investment_style === '가치투자자') {
            grantBadgeToUser(CURRENT_USER_ID, '가치투자 마스터', '가치투자 전문가');
        }
    }, 2000);
}

// === 전역 스코프로 함수 노출 ===
window.loadUserProfile = loadUserProfile;
window.saveProfile = saveProfile;
window.editProfile = editProfile;
window.initializeProfileAndBadges = initializeProfileAndBadges;
window.loadProfileTab = loadProfileTab;
window.testGrantBadges = testGrantBadges;

console.log('프로필 & 뱃지 시스템 JavaScript 모듈 로드 완료');