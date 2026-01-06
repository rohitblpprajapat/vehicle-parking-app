<template>
    <BaseModal :title="title" @close="handleClose">
        <div v-if="processing" class="text-center py-5">
            <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Processing...</span>
            </div>
            <h5 class="text-muted animate-pulse">Processing Payment...</h5>
            <p class="text-muted small">Please do not close this window</p>
        </div>

        <div v-else>
            <div class="alert alert-info d-flex align-items-center mb-4">
                <i class="bi bi-shield-lock-fill me-2 fs-4"></i>
                <div class="small">
                    This is a secure demo payment. No actual money will be deducted.
                </div>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-4 p-3 bg-light rounded border">
                <div>
                    <div class="text-uppercase text-muted extra-small fw-bold">Amount to Pay</div>
                    <div class="h3 mb-0 text-primary fw-bold">{{ $currency(amount) }}</div>
                </div>
                <div class="text-end">
                    <div class="d-flex gap-1">
                        <i class="bi bi-credit-card-2-front fs-3 text-secondary"></i>
                    </div>
                </div>
            </div>

            <form @submit.prevent="processPayment">
                <div class="mb-3">
                    <BaseInput
                        id="cardName"
                        v-model="form.name"
                        label="Cardholder Name"
                        placeholder="e.g. John Doe"
                        required
                    />
                </div>
                
                <div class="mb-3">
                    <BaseInput
                        id="cardNumber"
                        v-model="form.number"
                        label="Card Number"
                        placeholder="0000 0000 0000 0000"
                        required
                        maxlength="19"
                        @input="formatCardNumber"
                    />
                </div>

                <div class="row">
                    <div class="col-6">
                        <BaseInput
                            id="expiry"
                            v-model="form.expiry"
                            label="Expiry Date"
                            placeholder="MM/YY"
                            required
                            maxlength="5"
                            @input="formatExpiry"
                        />
                    </div>
                    <div class="col-6">
                        <BaseInput
                            id="cvv"
                            v-model="form.cvv"
                            label="CVV"
                            placeholder="123"
                            required
                            maxlength="3"
                            type="password"
                        />
                    </div>
                </div>

                <div class="text-danger mt-2 small" v-if="error">{{ error }}</div>
            </form>
        </div>

        <template #footer>
            <div class="d-flex w-100 gap-2" v-if="!processing">
                <BaseButton variant="secondary" class="flex-grow-1" @click="handleClose">Cancel</BaseButton>
                <BaseButton 
                    variant="success" 
                    class="flex-grow-1" 
                    @click="processPayment"
                    :disabled="!isValid"
                >
                    <i class="bi bi-lock-fill me-1"></i> Pay {{ $currency(amount) }}
                </BaseButton>
            </div>
        </template>
    </BaseModal>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'
import BaseModal from './BaseModal.vue'
import BaseInput from './BaseInput.vue'
import BaseButton from './BaseButton.vue'

const props = defineProps({
    amount: {
        type: Number,
        required: true
    },
    title: {
        type: String,
        default: 'Payment Gateway'
    }
})

const emit = defineEmits(['close', 'payment-success', 'payment-failed'])

const processing = ref(false)
const error = ref('')

const form = reactive({
    name: '',
    number: '',
    expiry: '',
    cvv: ''
})

const isValid = computed(() => {
    return form.name.length > 3 && 
           form.number.length >= 16 && 
           form.expiry.length === 5 && 
           form.cvv.length === 3
})

const formatCardNumber = (e) => {
    let value = e.target.value.replace(/\D/g, '')
    // Add space every 4 digits
    value = value.replace(/(\d{4})(?=\d)/g, '$1 ')
    form.number = value
}

const formatExpiry = (e) => {
    let value = e.target.value.replace(/\D/g, '')
    if (value.length > 2) {
        value = value.substring(0, 2) + '/' + value.substring(2, 4)
    }
    form.expiry = value
}

const handleClose = () => {
    if (!processing.value) {
        emit('close')
    }
}

const processPayment = () => {
    if (!isValid.value) return

    processing.value = true
    error.value = ''

    // Simulate API call delay
    setTimeout(() => {
        // Randomly fail 10% of the time for realism? No, let's keep it reliably successful for a demo.
        const success = true 
        
        if (success) {
            emit('payment-success', {
                transactionId: 'txn_' + Math.random().toString(36).substr(2, 9),
                amount: props.amount,
                timestamp: new Date().toISOString()
            })
        } else {
            error.value = 'Payment failed. Please try again.'
            processing.value = false
            emit('payment-failed')
        }
    }, 2000)
}
</script>

<style scoped>
.animate-pulse {
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}

.extra-small {
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}
</style>
