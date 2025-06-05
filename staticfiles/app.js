const { createApp } = Vue;

// Конфигурация API с автоопределением среды
const getApiBaseUrl = () => {
    // Определяем среду выполнения
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        if (port === '3000') {
            // Frontend в Docker (nginx на порту 3000)
            return '/api';  // Через nginx proxy
        } else if (port === '8000') {
            // Django development server
            return 'http://localhost:8000/api';
        } else {
            // http-server или другой статический сервер
            return 'http://localhost:8000/api';
        }
    } else {
        // Production или Docker Compose
        return '/api';
    }
};

const API_BASE_URL = getApiBaseUrl();

// Создание Vue приложения
createApp({
    data() {
        return {
            // Состояние аутентификации
            isAuthenticated: false,
            user: null,
            accessToken: null,
            
            // Состояние загрузки
            isLoading: false,
            
            // Сообщения
            successMessage: '',
            errorMessage: '',
            loginError: '',
            
            // Активная вкладка
            activeTab: 'list',
            
            // Формы
            loginForm: {
                username: '',
                password: ''
            },
            addForm: {
                equipment_type: '',
                serial_numbers_text: '',
                note: ''
            },
            editForm: {
                id: null,
                equipment_type: '',
                serial_number: '',
                note: ''
            },
            
            // Данные
            equipmentList: [],
            equipmentTypes: [],
            
            // Поиск и фильтрация
            searchQuery: '',
            selectedType: '',
            
            // Пагинация
            currentPage: 1,
            pagination: {
                count: 0,
                next: null,
                previous: null
            }
        };
    },
    
    mounted() {
        // Проверяем сохраненный токен при загрузке
        this.checkSavedAuth();
        console.log('API Base URL:', API_BASE_URL);
    },
    
    methods: {
        // === АУТЕНТИФИКАЦИЯ ===
        
        checkSavedAuth() {
            const token = localStorage.getItem('accessToken');
            const user = localStorage.getItem('user');
            
            if (token && user) {
                this.accessToken = token;
                this.user = JSON.parse(user);
                this.isAuthenticated = true;
                this.setupAxiosAuth();
                this.loadInitialData();
            }
        },
        
        setupAxiosAuth() {
            if (this.accessToken) {
                axios.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`;
            }
        },
        
        async login() {
            this.isLoading = true;
            this.loginError = '';
            
            try {
                const response = await axios.post(`${API_BASE_URL}/user/login/`, {
                    username: this.loginForm.username,
                    password: this.loginForm.password
                });
                
                this.accessToken = response.data.tokens.access;
                this.user = response.data.user;
                this.isAuthenticated = true;
                
                // Сохраняем в localStorage
                localStorage.setItem('accessToken', this.accessToken);
                localStorage.setItem('user', JSON.stringify(this.user));
                
                this.setupAxiosAuth();
                this.loadInitialData();
                
                this.showSuccess('Успешная авторизация!');
                
            } catch (error) {
                console.error('Login error:', error);
                this.loginError = error.response?.data?.error || 'Ошибка авторизации';
            } finally {
                this.isLoading = false;
            }
        },
        
        logout() {
            this.isAuthenticated = false;
            this.user = null;
            this.accessToken = null;
            
            localStorage.removeItem('accessToken');
            localStorage.removeItem('user');
            
            delete axios.defaults.headers.common['Authorization'];
            
            // Очищаем формы
            this.loginForm = { username: '', password: '' };
            this.equipmentList = [];
            this.equipmentTypes = [];
            
            this.showSuccess('Вы вышли из системы');
        },
        
        // === ЗАГРУЗКА ДАННЫХ ===
        
        async loadInitialData() {
            await Promise.all([
                this.loadEquipment(),
                this.loadEquipmentTypes()
            ]);
        },
        
        async loadEquipment(page = 1) {
            this.isLoading = true;
            
            try {
                const params = new URLSearchParams();
                params.append('page', page);
                
                if (this.searchQuery) {
                    params.append('search', this.searchQuery);
                }
                
                if (this.selectedType) {
                    params.append('equipment_type', this.selectedType);
                }
                
                const response = await axios.get(`${API_BASE_URL}/equipment/?${params}`);
                
                this.equipmentList = response.data.results;
                this.pagination = {
                    count: response.data.count,
                    next: response.data.next,
                    previous: response.data.previous
                };
                this.currentPage = page;
                
            } catch (error) {
                console.error('Load equipment error:', error);
                this.showError('Ошибка загрузки оборудования');
            } finally {
                this.isLoading = false;
            }
        },
        
        async loadEquipmentTypes() {
            try {
                const response = await axios.get(`${API_BASE_URL}/equipment/type/`);
                this.equipmentTypes = response.data.results || response.data;
            } catch (error) {
                console.error('Load equipment types error:', error);
                this.showError('Ошибка загрузки типов оборудования');
            }
        },
        
        // === ПОИСК И ФИЛЬТРАЦИЯ ===
        
        searchEquipment() {
            // Debounce поиска
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.loadEquipment(1);
            }, 500);
        },
        
        clearFilters() {
            this.searchQuery = '';
            this.selectedType = '';
            this.loadEquipment(1);
        },
        
        loadPage(page) {
            if (page > 0) {
                this.loadEquipment(page);
            }
        },
        
        // === CRUD ОПЕРАЦИИ ===
        
        async addEquipment() {
            this.isLoading = true;
            this.clearMessages();
            
            try {
                // Парсим серийные номера
                const serialNumbers = this.addForm.serial_numbers_text
                    .split('\n')
                    .map(s => s.trim())
                    .filter(s => s.length > 0);
                
                if (serialNumbers.length === 0) {
                    this.showError('Введите хотя бы один серийный номер');
                    return;
                }
                
                const data = {
                    equipment_type: parseInt(this.addForm.equipment_type),
                    serial_numbers: serialNumbers,
                    note: this.addForm.note || ''
                };
                
                const response = await axios.post(`${API_BASE_URL}/equipment/`, data);
                
                this.showSuccess(response.data.message || 'Оборудование успешно добавлено');
                
                // Очищаем форму
                this.addForm = {
                    equipment_type: '',
                    serial_numbers_text: '',
                    note: ''
                };
                
                // Обновляем список
                this.loadEquipment();
                this.loadEquipmentTypes(); // Обновляем счетчики
                
                // Переключаемся на список
                this.activeTab = 'list';
                
            } catch (error) {
                console.error('Add equipment error:', error);
                
                if (error.response?.data?.validation_errors) {
                    let errorMsg = 'Ошибки валидации:\n';
                    error.response.data.validation_errors.forEach(err => {
                        errorMsg += `• ${err.serial_number}: ${err.errors.join(', ')}\n`;
                    });
                    this.showError(errorMsg);
                } else {
                    this.showError(error.response?.data?.error || 'Ошибка добавления оборудования');
                }
            } finally {
                this.isLoading = false;
            }
        },
        
        editEquipment(equipment) {
            this.editForm = {
                id: equipment.id,
                equipment_type: equipment.equipment_type,
                serial_number: equipment.serial_number,
                note: equipment.note || ''
            };
            
            // Показываем модальное окно
            const modal = new bootstrap.Modal(document.getElementById('editModal'));
            modal.show();
        },
        
        async updateEquipment() {
            this.isLoading = true;
            this.clearMessages();
            
            try {
                const data = {
                    equipment_type: parseInt(this.editForm.equipment_type),
                    serial_number: this.editForm.serial_number,
                    note: this.editForm.note || ''
                };
                
                await axios.put(`${API_BASE_URL}/equipment/${this.editForm.id}/`, data);
                
                this.showSuccess('Оборудование успешно обновлено');
                
                // Закрываем модальное окно
                const modal = bootstrap.Modal.getInstance(document.getElementById('editModal'));
                modal.hide();
                
                // Обновляем список
                this.loadEquipment();
                
            } catch (error) {
                console.error('Update equipment error:', error);
                this.showError(error.response?.data?.error || 'Ошибка обновления оборудования');
            } finally {
                this.isLoading = false;
            }
        },
        
        async deleteEquipment(equipmentId) {
            if (!confirm('Вы уверены, что хотите удалить это оборудование?')) {
                return;
            }
            
            this.isLoading = true;
            this.clearMessages();
            
            try {
                await axios.delete(`${API_BASE_URL}/equipment/${equipmentId}/`);
                
                this.showSuccess('Оборудование успешно удалено');
                
                // Обновляем список
                this.loadEquipment();
                this.loadEquipmentTypes(); // Обновляем счетчики
                
            } catch (error) {
                console.error('Delete equipment error:', error);
                this.showError(error.response?.data?.error || 'Ошибка удаления оборудования');
            } finally {
                this.isLoading = false;
            }
        },
        
        // === УТИЛИТЫ ===
        
        formatDate(dateString) {
            if (!dateString) return '';
            
            const date = new Date(dateString);
            return date.toLocaleDateString('ru-RU', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        showSuccess(message) {
            this.successMessage = message;
            this.errorMessage = '';
            setTimeout(() => {
                this.successMessage = '';
            }, 5000);
        },
        
        showError(message) {
            this.errorMessage = message;
            this.successMessage = '';
            setTimeout(() => {
                this.errorMessage = '';
            }, 8000);
        },
        
        clearMessages() {
            this.successMessage = '';
            this.errorMessage = '';
            this.loginError = '';
        }
    }
}).mount('#app'); 